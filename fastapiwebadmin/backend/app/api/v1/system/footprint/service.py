# -*- coding: utf-8 -*-
"""会员足迹业务层"""

import typing
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from app.api.v1.system.footprint.model import Footprint
from app.api.v1.system.footprint.schema import FootprintIn, FootprintQuery

EXPORT_HEADERS = ["足迹ID", "用户ID", "商品ID", "添加时间"]


class FootprintService:
    """会员足迹管理"""

    @staticmethod
    async def list(params: FootprintQuery) -> typing.Dict[str, typing.Any]:
        return await Footprint.get_list(params)

    @staticmethod
    async def detail(footprint_id: int) -> typing.Dict[str, typing.Any]:
        footprint = await Footprint.get(footprint_id, to_dict=True)
        if not footprint:
            raise ValueError("足迹记录不存在")
        return footprint

    @staticmethod
    async def save_or_update(params: FootprintIn) -> None:
        payload = params.model_dump()
        if not payload.get("member_id"):
            raise ValueError("用户ID不能为空")
        if not payload.get("goods_id"):
            raise ValueError("商品ID不能为空")

        # 足迹是浏览记录，同一商品可重复产生，不做唯一性校验
        if not payload.get("id"):
            await Footprint.create(payload)
            return

        current = await Footprint.get(payload["id"])
        if not current:
            raise ValueError("足迹记录不存在")
        await Footprint.update(payload)

    @staticmethod
    async def deleted(footprint_id: int) -> int:
        return await Footprint.delete(footprint_id, True)

    @staticmethod
    async def export(params: FootprintQuery) -> tuple[bytes, str]:
        rows = await Footprint.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "会员足迹"

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
        return buffer.getvalue(), f"会员足迹_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
