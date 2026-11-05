# -*- coding: utf-8 -*-
"""通用问题业务层"""

import typing
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from app.api.v1.system.faq.model import Faq
from app.api.v1.system.faq.schema import FaqIn, FaqQuery

EXPORT_HEADERS = ["问题ID", "问题内容", "问题回复"]


class FaqService:
    """通用问题管理"""

    @staticmethod
    async def list(params: FaqQuery) -> typing.Dict[str, typing.Any]:
        return await Faq.get_list(params)

    @staticmethod
    async def detail(faq_id: int) -> typing.Dict[str, typing.Any]:
        faq = await Faq.get(faq_id, to_dict=True)
        if not faq:
            raise ValueError("问题不存在")
        return faq

    @staticmethod
    async def save_or_update(params: FaqIn) -> typing.Dict[str, typing.Any]:
        payload = params.model_dump()

        question = (payload.get("question") or "").strip()
        answer = (payload.get("answer") or "").strip()
        if not question:
            raise ValueError("问题不能为空")
        if not answer:
            raise ValueError("回复不能为空")

        payload["question"] = question
        payload["answer"] = answer

        if not payload.get("id"):
            created = await Faq.create(payload, to_dict=True)
            return {"id": created.get("id") if created else None}

        current = await Faq.get(payload["id"])
        if not current:
            raise ValueError("问题不存在")
        await Faq.update(payload)
        return {"id": payload["id"]}

    @staticmethod
    async def deleted(faq_id: int) -> int:
        # 物理删除
        return await Faq.delete(faq_id, True)

    @staticmethod
    async def export(params: FaqQuery) -> tuple[bytes, str]:
        rows = await Faq.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "通用问题"

        header_fill = PatternFill("solid", fgColor="F2F5F8")
        header_font = Font(bold=True, color="333333")
        center = Alignment(horizontal="center", vertical="center")

        sheet.append(EXPORT_HEADERS)
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center

        for row in rows:
            sheet.append([row.get("id"), row.get("question") or "", row.get("answer") or ""])

        widths = [10, 46, 80]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"通用问题_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
