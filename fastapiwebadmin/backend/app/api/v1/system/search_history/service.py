# -*- coding: utf-8 -*-
"""会员搜索历史业务层"""

import typing
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import delete

from app.api.v1.system.search_history.model import SearchHistory
from app.api.v1.system.search_history.schema import SearchHistoryIn, SearchHistoryQuery
from app.database.sqlalchemy import async_session_factory
from app.utils.current_user import current_user

EXPORT_HEADERS = ["搜索ID", "用户ID", "关键字", "添加时间"]


class SearchHistoryService:
    """会员搜索历史管理"""

    @staticmethod
    async def list(params: SearchHistoryQuery) -> typing.Dict[str, typing.Any]:
        return await SearchHistory.get_list(params)

    @staticmethod
    async def detail(history_id: int) -> typing.Dict[str, typing.Any]:
        history = await SearchHistory.get(history_id, to_dict=True)
        if not history:
            raise ValueError("搜索记录不存在")
        return history

    @staticmethod
    async def save_or_update(params: SearchHistoryIn) -> None:
        payload = params.model_dump()
        if not payload.get("member_id"):
            raise ValueError("用户ID不能为空")
        if not payload.get("keyword"):
            raise ValueError("搜索关键字不能为空")

        # 搜索历史允许重复（同一关键字可被多次搜索）
        if not payload.get("id"):
            await SearchHistory.create(payload)
            return

        current = await SearchHistory.get(payload["id"])
        if not current:
            raise ValueError("搜索记录不存在")
        await SearchHistory.update(payload)

    @staticmethod
    async def deleted(history_id: int) -> int:
        return await SearchHistory.delete(history_id, True)

    # ---------------------------------------------------------------- 客户端（会员本人）
    @staticmethod
    async def _member_id() -> int:
        user = await current_user()
        member_id = (user or {}).get("member_id")
        if not member_id:
            raise ValueError("登录信息已失效，请重新登录")
        return int(member_id)

    @staticmethod
    async def my_list(limit: int = 20) -> typing.List[typing.Dict[str, typing.Any]]:
        member_id = await SearchHistoryService._member_id()
        rows = await SearchHistory.get_result(SearchHistory.my_stmt(member_id, limit)) or []
        seen, result = set(), []
        for row in rows:
            keyword = (row.get("keyword") or "").strip()
            if not keyword or keyword in seen:
                continue
            seen.add(keyword)
            result.append({"id": row.get("id"), "keyword": keyword})
        return result[:10]

    @staticmethod
    async def add(keyword: str) -> typing.Dict[str, typing.Any]:
        member_id = await SearchHistoryService._member_id()
        value = (keyword or "").strip()
        if not value:
            raise ValueError("搜索关键字不能为空")
        async with async_session_factory() as session, session.begin():
            # 同一个关键字只保留最新一条，避免历史里全是重复项
            await session.execute(
                delete(SearchHistory).where(
                    SearchHistory.member_id == member_id, SearchHistory.keyword == value
                )
            )
            session.add(SearchHistory(member_id=member_id, keyword=value, enabled_flag=True))
        return {"keyword": value}

    @staticmethod
    async def clear() -> int:
        member_id = await SearchHistoryService._member_id()
        async with async_session_factory() as session, session.begin():
            result = await session.execute(
                delete(SearchHistory).where(SearchHistory.member_id == member_id)
            )
            return result.rowcount

    @staticmethod
    async def export(params: SearchHistoryQuery) -> tuple[bytes, str]:
        rows = await SearchHistory.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "搜索历史"

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
                    row.get("keyword") or "",
                    row.get("creation_date") or "",
                ]
            )

        widths = [12, 14, 24, 24]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"搜索历史_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
