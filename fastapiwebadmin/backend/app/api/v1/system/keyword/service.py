# -*- coding: utf-8 -*-
"""搜索关键词业务层"""

import typing
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from app.api.v1.system.keyword.model import Keyword
from app.api.v1.system.keyword.schema import KeywordIn, KeywordQuery

YES_NO = {1: "是", 0: "否"}
EXPORT_HEADERS = ["关键词ID", "关键词", "跳转链接", "是否推荐", "是否默认"]


class KeywordService:
    """搜索关键词管理"""

    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        row["is_recommend_text"] = YES_NO.get(row.get("is_recommend"), "否")
        row["is_default_text"] = YES_NO.get(row.get("is_default"), "否")
        return row

    @staticmethod
    async def list(params: KeywordQuery) -> typing.Dict[str, typing.Any]:
        data = await Keyword.get_list(params)
        for row in data.get("rows", []):
            KeywordService._decorate(row)
        return data

    @staticmethod
    async def detail(keyword_id: int) -> typing.Dict[str, typing.Any]:
        row = await Keyword.get(keyword_id, to_dict=True)
        if not row:
            raise ValueError("关键词不存在")
        return KeywordService._decorate(row)

    @staticmethod
    async def save_or_update(params: KeywordIn) -> typing.Dict[str, typing.Any]:
        payload = params.model_dump()

        keyword = (payload.get("keyword") or "").strip()
        if not keyword:
            raise ValueError("关键词不能为空")
        payload["keyword"] = keyword

        if not payload.get("id"):
            created = await Keyword.create(payload, to_dict=True)
            return {"id": created.get("id") if created else None}

        current = await Keyword.get(payload["id"])
        if not current:
            raise ValueError("关键词不存在")
        await Keyword.update(payload)
        return {"id": payload["id"]}

    @staticmethod
    async def deleted(keyword_id: int) -> int:
        # 物理删除
        return await Keyword.delete(keyword_id, True)

    @staticmethod
    async def export(params: KeywordQuery) -> tuple[bytes, str]:
        rows = await Keyword.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "搜索关键词"

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
                    row.get("keyword") or "",
                    row.get("link") or "",
                    YES_NO.get(row.get("is_recommend"), "否"),
                    YES_NO.get(row.get("is_default"), "否"),
                ]
            )

        widths = [12, 24, 50, 12, 12]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"关键词_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
