# -*- coding: utf-8 -*-
"""收货地址业务层"""

import typing
import re
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import delete, select, update

from app.api.v1.system.address.model import Address
from app.api.v1.system.address.schema import AddressIn, AddressQuery
from app.api.v1.system.cart.service import CartService
from app.api.v1.system.region.model import Region
from app.database.sqlalchemy import async_session_factory

DEFAULT_TEXT = {1: "是", 0: "否"}

EXPORT_HEADERS = ["地址ID", "用户ID", "收货人名称", "手机号码", "区域地址", "详细地址", "默认"]


class AddressService:
    """收货地址管理"""

    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        row["is_default_name"] = DEFAULT_TEXT.get(row.get("is_default"), "否")
        return row

    @staticmethod
    async def list(params: AddressQuery) -> typing.Dict[str, typing.Any]:
        data = await Address.get_list(params)
        for row in data.get("rows", []):
            AddressService._decorate(row)
        return data

    @staticmethod
    async def detail(address_id: int) -> typing.Dict[str, typing.Any]:
        address = await Address.get(address_id, to_dict=True)
        if not address:
            raise ValueError("收货地址不存在")
        return AddressService._decorate(address)

    @staticmethod
    async def save_or_update(params: AddressIn) -> None:
        raise ValueError("收货地址仅支持会员本人维护")

    @staticmethod
    async def deleted(address_id: int) -> int:
        raise ValueError("收货地址仅支持会员本人维护")

    # ------------------------------------------------------------------ 会员本人维护
    @staticmethod
    def client_row(row, region_ids=None) -> typing.Dict[str, typing.Any]:
        """结算与地址页面共用的公开投影，不返回会员ID或审计字段。"""
        def value(key, default=None):
            return row.get(key, default) if isinstance(row, dict) else getattr(row, key, default)
        return {
            "id": value("id"),
            "receiver_name": value("receiver_name") or "",
            "mobile": value("mobile") or "",
            "region": value("region") or "",
            "detail": value("detail") or "",
            "is_default": bool(value("is_default")),
            "region_ids": list(region_ids or []),
        }

    @staticmethod
    async def _region_paths(session):
        """从现有有效行政区域构建完整路径，用于校验和旧地址回显。"""
        regions = (await session.scalars(select(Region).where(Region.enabled_flag.is_(True)))).all()
        by_id = {region.id: region for region in regions}
        paths = {}
        for district in regions:
            if district.level != 3:
                continue
            city = by_id.get(district.parent_id)
            province = by_id.get(city.parent_id) if city and city.level == 2 else None
            if province and province.level == 1 and province.parent_id == 0:
                paths[(province.id, city.id, district.id)] = [province.name, city.name, district.name]
        return paths

    @staticmethod
    def _resolve_region_ids(region: str, paths) -> typing.List[int]:
        # 兼容原有地址使用空格、斜杠或直接拼接的区域名称。
        normalized = re.sub(r"[\s/／>，,]+", "", region or "")
        for ids, names in paths.items():
            if normalized == "".join(names):
                return list(ids)
        return []

    @staticmethod
    async def _own_address(session, member_id, address_id, lock=False):
        stmt = select(Address).where(
            Address.id == address_id, Address.member_id == member_id,
            Address.enabled_flag.is_(True),
        )
        if lock:
            stmt = stmt.with_for_update()
        row = await session.scalar(stmt)
        if not row:
            raise ValueError("收货地址不存在或不属于当前会员")
        return row

    @staticmethod
    async def my_list():
        member_id = await CartService._member_id()
        async with async_session_factory() as session:
            await CartService._member(session, member_id)
            rows = (await session.scalars(Address.my_stmt(member_id))).all()
            paths = await AddressService._region_paths(session)
            result = [AddressService.client_row(row, AddressService._resolve_region_ids(row.region, paths)) for row in rows]
            default = next((row["id"] for row in result if row["is_default"]), None)
            return {"rows": result, "rowTotal": len(result), "default_id": default}

    @staticmethod
    async def my_detail(address_id):
        member_id = await CartService._member_id()
        async with async_session_factory() as session:
            await CartService._member(session, member_id)
            row = await AddressService._own_address(session, member_id, address_id)
            paths = await AddressService._region_paths(session)
            return AddressService.client_row(row, AddressService._resolve_region_ids(row.region, paths))

    @staticmethod
    async def my_save(params):
        member_id = await CartService._member_id()
        name, detail, mobile = params.receiver_name.strip(), params.detail.strip(), params.mobile.strip()
        if not name or len(name) > 64 or not detail or len(detail) > 255:
            raise ValueError("请填写有效的收货人和详细地址")
        if not re.fullmatch(r"1[3-9]\d{9}", mobile):
            raise ValueError("请输入正确的11位手机号码")
        async with async_session_factory() as session, session.begin():
            await CartService._member(session, member_id, lock=True)
            paths = await AddressService._region_paths(session)
            region_names = paths.get(tuple(params.region_ids))
            if not region_names:
                raise ValueError("请选择有效且完整的省市区")
            row = await AddressService._own_address(session, member_id, params.id, lock=True) if params.id else None
            current_default = await session.scalar(select(Address.id).where(
                Address.member_id == member_id, Address.enabled_flag.is_(True), Address.is_default == 1,
            ).order_by(Address.id).limit(1))
            make_default = bool(params.is_default or current_default is None)
            if make_default:
                await session.execute(update(Address).where(
                    Address.member_id == member_id, Address.enabled_flag.is_(True),
                ).values(is_default=0))
            payload = {
                "receiver_name": name, "mobile": mobile, "region": " ".join(region_names),
                "detail": detail, "is_default": int(make_default),
            }
            if row is None:
                row = Address(**await Address.handle_params({**payload, "member_id": member_id}))
                session.add(row)
            else:
                for key, value in payload.items():
                    setattr(row, key, value)
            await session.flush()
            return AddressService.client_row(row, params.region_ids)

    @staticmethod
    async def my_default(address_id):
        member_id = await CartService._member_id()
        async with async_session_factory() as session, session.begin():
            await CartService._member(session, member_id, lock=True)
            row = await AddressService._own_address(session, member_id, address_id, lock=True)
            await session.execute(update(Address).where(
                Address.member_id == member_id, Address.enabled_flag.is_(True),
            ).values(is_default=0))
            row.is_default = 1
            await session.flush()
            paths = await AddressService._region_paths(session)
            return AddressService.client_row(row, AddressService._resolve_region_ids(row.region, paths))

    @staticmethod
    async def my_deleted(address_id):
        member_id = await CartService._member_id()
        async with async_session_factory() as session, session.begin():
            await CartService._member(session, member_id, lock=True)
            row = await AddressService._own_address(session, member_id, address_id, lock=True)
            was_default = bool(row.is_default)
            await session.execute(delete(Address).where(Address.id == row.id, Address.member_id == member_id))
            if was_default:
                first = await session.scalar(select(Address).where(
                    Address.member_id == member_id, Address.enabled_flag.is_(True),
                ).order_by(Address.id).limit(1))
                if first:
                    await session.execute(update(Address).where(
                        Address.member_id == member_id, Address.enabled_flag.is_(True),
                    ).values(is_default=0))
                    first.is_default = 1
            await session.flush()

    @staticmethod
    async def export(params: AddressQuery) -> tuple[bytes, str]:
        rows = await Address.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "收货地址"

        header_fill = PatternFill("solid", fgColor="F2F5F8")
        header_font = Font(bold=True, color="333333")
        center = Alignment(horizontal="center", vertical="center")

        sheet.append(EXPORT_HEADERS)
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center

        for row in rows:
            sheet.append(
                [
                    row.get("id"),
                    row.get("member_id"),
                    row.get("receiver_name") or "",
                    row.get("mobile") or "",
                    row.get("region") or "",
                    row.get("detail") or "",
                    DEFAULT_TEXT.get(row.get("is_default"), "否"),
                ]
            )

        widths = [12, 12, 16, 18, 32, 32, 8]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"收货地址_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
