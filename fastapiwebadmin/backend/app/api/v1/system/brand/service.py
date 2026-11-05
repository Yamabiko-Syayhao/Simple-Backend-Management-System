# -*- coding: utf-8 -*-
"""品牌制造商业务层"""

import typing
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import select

from app.api.v1.system.brand.model import Brand
from app.api.v1.system.brand.schema import BrandIn, BrandQuery

EXPORT_HEADERS = ["品牌商ID", "品牌商名称", "介绍", "底价", "品牌商图片"]


class BrandService:
    """品牌制造商管理"""

    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """把 Decimal 底价转成 float，前端直接展示"""
        price = row.get("floor_price")
        row["floor_price"] = float(price) if price is not None else None
        return row

    @staticmethod
    async def list(params: BrandQuery) -> typing.Dict[str, typing.Any]:
        data = await Brand.get_list(params)
        for row in data.get("rows", []):
            BrandService._decorate(row)
        return data

    @staticmethod
    async def detail(brand_id: int) -> typing.Dict[str, typing.Any]:
        brand = await Brand.get(brand_id, to_dict=True)
        if not brand:
            raise ValueError("品牌商不存在")
        return BrandService._decorate(brand)

    @staticmethod
    async def save_or_update(params: BrandIn) -> typing.Dict[str, typing.Any]:
        payload = params.model_dump()
        if not payload.get("name"):
            raise ValueError("品牌商名称不能为空")

        # 名称不允许重复
        exists = await Brand.get_result(
            select(Brand.id).where(
                Brand.name == payload["name"], Brand.enabled_flag.is_(True)
            ),
            first=True,
        )
        if exists and exists["id"] != payload.get("id"):
            raise ValueError("品牌商名称已存在")

        if not payload.get("id"):
            created = await Brand.create(payload, to_dict=True)
            return {"id": created.get("id") if created else None}

        current = await Brand.get(payload["id"])
        if not current:
            raise ValueError("品牌商不存在")
        await Brand.update(payload)
        return {"id": payload["id"]}

    @staticmethod
    async def deleted(brand_id: int) -> int:
        # 物理删除：直接从 mal_brand 表中移除（不走 enabled_flag 逻辑删除）
        return await Brand.delete(brand_id, True)

    # ---------------------------------------------------------------- 客户端（只读）
    CLIENT_FIELDS = ("id", "name", "image", "description", "floor_price")

    @staticmethod
    async def client_list(params: BrandQuery) -> typing.Dict[str, typing.Any]:
        data = await Brand.get_list(params)
        data["rows"] = [
            BrandService._decorate({key: row.get(key) for key in BrandService.CLIENT_FIELDS})
            for row in data.get("rows", [])
        ]
        return data

    @staticmethod
    async def client_detail(brand_id: int) -> typing.Dict[str, typing.Any]:
        brand = await BrandService.detail(brand_id)
        return {key: brand.get(key) for key in BrandService.CLIENT_FIELDS}

    @staticmethod
    async def export(params: BrandQuery) -> tuple[bytes, str]:
        rows = await Brand.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "品牌制造商"

        header_fill = PatternFill("solid", fgColor="F2F5F8")
        header_font = Font(bold=True, color="333333")
        center = Alignment(horizontal="center", vertical="center")

        sheet.append(EXPORT_HEADERS)
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center

        for row in rows:
            price = row.get("floor_price")
            sheet.append(
                [
                    row.get("id"),
                    row.get("name") or "",
                    row.get("description") or "",
                    float(price) if price is not None else "",
                    row.get("image") or "",
                ]
            )

        widths = [12, 22, 60, 10, 40]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"品牌制造商_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
