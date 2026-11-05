# -*- coding: utf-8 -*-
"""售后管理业务层"""

import typing
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import update

from app.api.v1.system.after_sale.model import AfterSale
from app.api.v1.system.after_sale.schema import AfterSaleAuditIn, AfterSaleQuery

STATUS_TEXT = {
    1: "待审核",
    2: "待退款",
    3: "已拒绝",
    4: "已退款",
}

EXPORT_HEADERS = ["售后编号", "订单ID", "订单编号", "用户ID", "用户昵称", "售后类型", "退款原因", "退款价格", "状态", "申请时间"]


class AfterSaleService:
    """售后管理"""

    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        row["status_name"] = STATUS_TEXT.get(row.get("status"), "未知")
        if row.get("refund_amount") is not None:
            row["refund_amount"] = float(row["refund_amount"])
        return row

    @staticmethod
    async def list(params: AfterSaleQuery) -> typing.Dict[str, typing.Any]:
        data = await AfterSale.get_list(params)
        for row in data.get("rows", []):
            AfterSaleService._decorate(row)
        return data

    @staticmethod
    async def detail(after_sale_id: int) -> typing.Dict[str, typing.Any]:
        row = await AfterSale.get(after_sale_id, to_dict=True)
        if not row:
            raise ValueError("售后记录不存在")
        return AfterSaleService._decorate(row)

    @staticmethod
    async def audit(params: AfterSaleAuditIn) -> int:
        ids = [int(i) for i in (params.ids or []) if i]
        if not ids:
            raise ValueError("请选择至少一条记录")
        if params.action not in ("pass", "reject"):
            raise ValueError("参数不对")

        # 通过 → 待退款；拒绝 → 已拒绝
        target_status = 2 if params.action == "pass" else 3
        stmt = (
            update(AfterSale)
            .where(AfterSale.id.in_(ids), AfterSale.enabled_flag.is_(True))
            .values(
                status=target_status,
                audit_time=datetime.now(),
                audit_remark=params.remark or "",
            )
        )
        result = await AfterSale.execute(stmt)
        if not result.rowcount:
            raise ValueError("所选记录不存在或已处理")
        return result.rowcount

    @staticmethod
    async def export(params: AfterSaleQuery) -> tuple[bytes, str]:
        rows = await AfterSale.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "售后管理"

        header_fill = PatternFill("solid", fgColor="F2F5F8")
        header_font = Font(bold=True, color="333333")
        center = Alignment(horizontal="center", vertical="center")

        sheet.append(EXPORT_HEADERS)
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center

        for row in rows:
            amount = row.get("refund_amount")
            sheet.append(
                [
                    row.get("after_sale_no") or "",
                    row.get("order_id"),
                    row.get("order_no") or "",
                    row.get("member_id"),
                    row.get("username") or "",
                    row.get("type") or "",
                    row.get("reason") or "",
                    float(amount) if amount is not None else "",
                    STATUS_TEXT.get(row.get("status"), ""),
                    row.get("apply_time") or "",
                ]
            )

        widths = [20, 12, 20, 12, 14, 14, 36, 12, 10, 20]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"售后管理_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
