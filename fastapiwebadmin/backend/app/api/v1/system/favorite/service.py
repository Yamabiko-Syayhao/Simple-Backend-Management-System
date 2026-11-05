# -*- coding: utf-8 -*-
"""会员收藏业务层"""

import typing
from datetime import datetime
from io import BytesIO
from decimal import Decimal

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import select

from app.api.v1.system.favorite.model import Favorite
from app.api.v1.system.favorite.schema import FavoriteIn, FavoriteQuery

EXPORT_HEADERS = ["收藏ID", "用户ID", "商品ID", "添加时间"]


class FavoriteService:
    """会员收藏管理"""

    @staticmethod
    async def my_list(params):
        from app.api.v1.system.cart.service import CartService
        from app.database.sqlalchemy import async_session_factory

        member_id = await CartService._member_id()
        async with async_session_factory() as session:
            await CartService._member(session, member_id)
            data = await Favorite.get_member_list(params, member_id)
            for row in data["rows"]:
                exists = bool(row.pop("goods_enabled"))
                on_sale = bool(row.pop("is_on_sale"))
                reason = "商品已删除" if not exists else ("商品已下架" if not on_sale else "")
                price = Decimal(str(row.get("retail_price") or 0)).quantize(Decimal("0.01"))
                row.update({"name": (row.get("name") or "商品已删除") if exists else "商品已删除",
                            "image": (row.get("image") or "") if exists else "",
                            "brief": (row.get("brief") or "") if exists else "",
                            "retail_price": float(price) if exists else 0,
                            "retail_price_text": format(price if exists else Decimal(0), ".2f"),
                            "available": not bool(reason), "invalid_reason": reason})
            return data

    @staticmethod
    async def my_deleted(favorite_id: int):
        from sqlalchemy import delete
        from app.api.v1.system.cart.service import CartService
        from app.database.sqlalchemy import async_session_factory

        member_id = await CartService._member_id()
        async with async_session_factory() as session, session.begin():
            await CartService._member(session, member_id, lock=True)
            favorite = await session.scalar(select(Favorite).where(Favorite.id == favorite_id,
                Favorite.member_id == member_id, Favorite.enabled_flag.is_(True)).with_for_update())
            if not favorite:
                raise ValueError("收藏记录不存在或不属于当前用户")
            await session.execute(delete(Favorite).where(Favorite.id == favorite.id))
            return {}

    @staticmethod
    async def my_set(params):
        from sqlalchemy import delete
        from app.api.v1.system.cart.service import CartService
        from app.api.v1.system.goods.model import Goods
        from app.database.sqlalchemy import async_session_factory

        member_id = await CartService._member_id()
        async with async_session_factory() as session, session.begin():
            # 同一会员设置收藏串行，重复请求不会新增多行。
            await CartService._member(session, member_id, lock=True)
            favorites = (await session.scalars(select(Favorite).where(Favorite.member_id == member_id,
                Favorite.goods_id == params.goods_id).with_for_update())).all()
            if params.collected:
                goods = await session.get(Goods, params.goods_id)
                if not goods or not goods.enabled_flag or not goods.is_on_sale:
                    raise ValueError("商品不存在或已下架")
                live = next((row for row in favorites if row.enabled_flag), None)
                if not live:
                    session.add(Favorite(member_id=member_id, goods_id=params.goods_id))
            else:
                # 按本人+商品取消，兼容历史重复记录；从不删除商品本身。
                await session.execute(delete(Favorite).where(Favorite.member_id == member_id, Favorite.goods_id == params.goods_id))
            return {"goods_id": params.goods_id, "collected": params.collected}

    @staticmethod
    async def list(params: FavoriteQuery) -> typing.Dict[str, typing.Any]:
        return await Favorite.get_list(params)

    @staticmethod
    async def detail(favorite_id: int) -> typing.Dict[str, typing.Any]:
        favorite = await Favorite.get(favorite_id, to_dict=True)
        if not favorite:
            raise ValueError("收藏记录不存在")
        return favorite

    @staticmethod
    async def save_or_update(params: FavoriteIn) -> None:
        payload = params.model_dump()
        if not payload.get("member_id"):
            raise ValueError("用户ID不能为空")
        if not payload.get("goods_id"):
            raise ValueError("商品ID不能为空")

        # 同一会员对同一商品只允许收藏一次
        stmt = select(Favorite.id).where(
            Favorite.member_id == payload["member_id"],
            Favorite.goods_id == payload["goods_id"],
            Favorite.enabled_flag.is_(True),
        )
        if payload.get("id"):
            stmt = stmt.where(Favorite.id != payload["id"])
        if await Favorite.get_result(stmt, first=True):
            raise ValueError("该用户已收藏过该商品")

        if not payload.get("id"):
            await Favorite.create(payload)
            return

        current = await Favorite.get(payload["id"])
        if not current:
            raise ValueError("收藏记录不存在")
        await Favorite.update(payload)

    @staticmethod
    async def deleted(favorite_id: int) -> int:
        # 物理删除：直接从 mal_favorite 表中移除
        return await Favorite.delete(favorite_id, True)

    @staticmethod
    async def export(params: FavoriteQuery) -> tuple[bytes, str]:
        rows = await Favorite.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "会员收藏"

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
                    row.get("goods_id"),
                    row.get("creation_date") or "",
                ]
            )

        widths = [12, 14, 16, 24]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"会员收藏_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
