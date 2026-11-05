# -*- coding: utf-8 -*-
"""会员意见反馈业务层"""

import typing
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from app.api.v1.system.feedback.model import Feedback
from app.api.v1.system.feedback.schema import FeedbackIn, FeedbackQuery

EXPORT_HEADERS = ["反馈ID", "用户名", "手机号码", "反馈类型", "反馈内容", "反馈图片", "时间"]


class FeedbackService:
    """会员意见反馈管理"""

    @staticmethod
    async def my_submit(params):
        from app.api.v1.system.cart.service import CartService
        from app.database.sqlalchemy import async_session_factory

        content = params.content.strip()
        if not content:
            raise ValueError("反馈内容不能为空")
        member_id = await CartService._member_id()
        async with async_session_factory() as session, session.begin():
            member = await CartService._member(session, member_id, lock=True)
            feedback = Feedback(member_id=member_id, username=member.username, mobile=params.mobile or member.mobile,
                                feedback_type=params.feedback_type, content=content)
            session.add(feedback)
            await session.flush()
            return {"id": feedback.id}

    @staticmethod
    async def contact():
        from sqlalchemy import select
        from app.api.v1.system.cart.service import CartService
        from app.api.v1.system.lookup.model import Lookup, LookupValue
        from app.config.setting import settings
        from app.database.sqlalchemy import async_session_factory

        member_id = await CartService._member_id()
        async with async_session_factory() as session:
            await CartService._member(session, member_id)
            # 复用后台数据字典，只读取明确公开的服务信息，不返回配置全集。
            keys = ("name", "phone", "qq", "version", "agreement")
            rows = (await session.execute(select(LookupValue.lookup_code, LookupValue.lookup_value).join(
                Lookup, LookupValue.lookup_id == Lookup.id).where(Lookup.enabled_flag.is_(True),
                Lookup.code == "mall_public", LookupValue.enabled_flag.is_(True),
                LookupValue.lookup_code.in_(keys)).order_by(LookupValue.id))).all()
            values = {key: value or "" for key, value in rows}
            return {"name": values.get("name") or "商城服务中心", "phone": values.get("phone", ""),
                    "qq": values.get("qq", ""), "version": values.get("version") or settings.VERSION,
                    "agreement": values.get("agreement", ""),
                    "feedback_types": ["功能建议", "商品问题", "物流问题", "其他"]}

    @staticmethod
    async def list(params: FeedbackQuery) -> typing.Dict[str, typing.Any]:
        data = await Feedback.get_list(params)
        for row in data.get("rows", []):
            FeedbackService._decorate(row)
        return data

    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """把逗号分隔的图片串转成列表，便于前端直接渲染"""
        images = row.get("images") or ""
        row["image_list"] = [item for item in images.split(",") if item.strip()] if images else []
        return row

    @staticmethod
    async def detail(feedback_id: int) -> typing.Dict[str, typing.Any]:
        feedback = await Feedback.get(feedback_id, to_dict=True)
        if not feedback:
            raise ValueError("反馈记录不存在")
        return FeedbackService._decorate(feedback)

    @staticmethod
    async def save_or_update(params: FeedbackIn) -> None:
        payload = params.model_dump()
        if not payload.get("content"):
            raise ValueError("反馈内容不能为空")

        if not payload.get("id"):
            await Feedback.create(payload)
            return

        current = await Feedback.get(payload["id"])
        if not current:
            raise ValueError("反馈记录不存在")
        await Feedback.update(payload)

    @staticmethod
    async def deleted(feedback_id: int) -> int:
        return await Feedback.delete(feedback_id, True)

    @staticmethod
    async def export(params: FeedbackQuery) -> tuple[bytes, str]:
        rows = await Feedback.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "意见反馈"

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
                    row.get("username") or "",
                    row.get("mobile") or "",
                    row.get("feedback_type") or "",
                    row.get("content") or "",
                    row.get("images") or "",
                    row.get("creation_date") or "",
                ]
            )

        widths = [10, 16, 18, 14, 36, 36, 22]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"意见反馈_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
