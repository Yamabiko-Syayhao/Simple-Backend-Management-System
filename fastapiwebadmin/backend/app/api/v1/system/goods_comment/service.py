# -*- coding: utf-8 -*-
"""商品评论业务层"""

import typing
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from app.api.v1.system.goods_comment.model import GoodsComment
from app.api.v1.system.goods_comment.schema import GoodsCommentQuery, GoodsCommentReplyIn

EXPORT_HEADERS = ["评论ID", "用户ID", "商品ID", "打分", "评论内容", "评论图片", "评论时间", "商家回复", "回复时间"]


class GoodsCommentService:
    """商品评论管理"""

    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        images = row.get("images") or ""
        row["image_list"] = [item for item in images.split(",") if item]
        row["replied"] = bool(row.get("reply_content"))
        return row

    @staticmethod
    async def list(params: GoodsCommentQuery) -> typing.Dict[str, typing.Any]:
        data = await GoodsComment.get_list(params)
        for row in data.get("rows", []):
            GoodsCommentService._decorate(row)
        return data

    @staticmethod
    async def reply(params: GoodsCommentReplyIn) -> typing.Dict[str, typing.Any]:
        content = (params.content or "").strip()
        if not content:
            raise ValueError("回复内容不能为空")
        if not params.comment_id:
            raise ValueError("参数不对")

        comment = await GoodsComment.get(params.comment_id)
        if not comment:
            raise ValueError("评论不存在")
        # 一条评论只允许回复一次
        if comment.reply_content:
            raise ValueError("订单商品已回复！")

        await GoodsComment.update(
            {"id": params.comment_id, "reply_content": content, "reply_time": datetime.now()}
        )
        return {"comment_id": params.comment_id}

    @staticmethod
    async def deleted(comment_id: int) -> int:
        # 物理删除
        return await GoodsComment.delete(comment_id, True)

    @staticmethod
    async def export(params: GoodsCommentQuery) -> tuple[bytes, str]:
        rows = await GoodsComment.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "商品评论"

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
                    row.get("score"),
                    row.get("content") or "",
                    row.get("images") or "",
                    row.get("comment_time") or "",
                    row.get("reply_content") or "",
                    row.get("reply_time") or "",
                ]
            )

        widths = [10, 10, 12, 8, 50, 30, 20, 30, 20]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"商品评论_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
