# -*- coding: utf-8 -*-
"""团购活动业务层"""

import typing
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from app.api.v1.system.group_activity.model import GroupActivity, GroupActivityMember
from app.api.v1.system.group_activity.schema import GroupActivityQuery

EXPORT_HEADERS = [
    "活动ID", "团购规则ID", "订单ID", "用户ID",
    "参与人数", "团购折扣", "团购要求", "开始时间", "结束时间",
]


class GroupActivityService:
    """团购活动管理（后台只读：查看、筛选、导出）"""

    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        if row.get("discount") is not None:
            row["discount"] = float(row["discount"])
        return row

    @staticmethod
    async def list(params: GroupActivityQuery) -> typing.Dict[str, typing.Any]:
        data = await GroupActivity.get_list(params)
        rows = data.get("rows", [])
        for row in rows:
            GroupActivityService._decorate(row)

        # 挂上参与成员，供表格展开行显示
        members = await GroupActivityMember.get_by_activity_ids([row["id"] for row in rows])
        member_map: typing.Dict[int, typing.List[typing.Dict[str, typing.Any]]] = {}
        for member in members:
            member_map.setdefault(member["activity_id"], []).append(member)
        for row in rows:
            row["members"] = member_map.get(row["id"], [])
        return data

    @staticmethod
    async def export(params: GroupActivityQuery) -> tuple[bytes, str]:
        rows = await GroupActivity.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "团购活动"

        header_fill = PatternFill("solid", fgColor="F2F5F8")
        header_font = Font(bold=True, color="333333")
        center = Alignment(horizontal="center", vertical="center")

        sheet.append(EXPORT_HEADERS)
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center

        for row in rows:
            row = GroupActivityService._decorate(dict(row))
            sheet.append(
                [
                    row.get("id"),
                    row.get("rule_id"),
                    row.get("order_id"),
                    row.get("member_id"),
                    row.get("participants"),
                    row.get("discount"),
                    row.get("people"),
                    row.get("start_time") or "",
                    row.get("end_time") or "",
                ]
            )

        widths = [10, 14, 12, 12, 12, 12, 12, 22, 22]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"团购活动_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
