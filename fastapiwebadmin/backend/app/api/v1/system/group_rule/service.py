# -*- coding: utf-8 -*-
"""团购规则业务层"""

import typing
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import select

from app.api.v1.system.goods.model import Goods
from app.api.v1.system.group_rule.model import GroupRule
from app.api.v1.system.group_rule.schema import GroupRuleIn, GroupRuleQuery
from app.database.sqlalchemy import async_session_factory

EXPORT_HEADERS = ["团购规则ID", "商品ID", "商品编号", "商品名称", "团购优惠", "团购人数要求", "状态", "结束时间"]


def _to_datetime(value) -> typing.Optional[datetime]:
    """查询结果统一走序列化，datetime 可能已变成字符串，这里还原后再比较"""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


class GroupRuleService:
    """团购规则管理"""

    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        if row.get("discount") is not None:
            row["discount"] = float(row["discount"])
        end_time = _to_datetime(row.get("end_time"))
        expired = bool(end_time) and end_time < datetime.now()
        row["status"] = 1 if expired else 0
        row["status_text"] = "到期下线" if expired else "进行中"
        return row

    @staticmethod
    async def list(params: GroupRuleQuery) -> typing.Dict[str, typing.Any]:
        data = await GroupRule.get_list(params)
        for row in data.get("rows", []):
            GroupRuleService._decorate(row)
        return data

    @staticmethod
    async def detail(rule_id: int) -> typing.Dict[str, typing.Any]:
        async with async_session_factory() as session:
            rule = await session.get(GroupRule, rule_id)
            if not rule:
                raise ValueError("团购规则不存在")
            goods = await session.get(Goods, rule.goods_id)
            data = {
                "id": rule.id,
                "goods_id": rule.goods_id,
                "discount": float(rule.discount) if rule.discount is not None else 0,
                "people": rule.people,
                "end_time": rule.end_time,
                "goods_name": goods.name if goods else "",
                "goods_image": goods.image if goods else "",
                "goods_sn": goods.goods_sn if goods else "",
            }
        return GroupRuleService._decorate(data)

    @staticmethod
    async def save_or_update(params: GroupRuleIn) -> typing.Dict[str, typing.Any]:
        if not params.goods_id:
            raise ValueError("商品ID不能为空")
        if not params.end_time:
            raise ValueError("请选择过期时间")

        async with async_session_factory() as session, session.begin():
            goods = await session.get(Goods, params.goods_id)
            if not goods:
                raise ValueError("商品不存在")

            if params.id:
                row = await session.get(GroupRule, params.id)
                if not row:
                    raise ValueError("团购规则不存在")
                row.goods_id = params.goods_id
                row.discount = params.discount
                row.people = params.people
                row.end_time = params.end_time
            else:
                row = GroupRule(
                    goods_id=params.goods_id,
                    discount=params.discount,
                    people=params.people,
                    end_time=params.end_time,
                    enabled_flag=True,
                )
                session.add(row)
            await session.flush()
            return {"id": row.id}

    @staticmethod
    async def deleted(rule_id: int) -> int:
        # 物理删除
        return await GroupRule.delete(rule_id, True)

    # ---------------------------------------------------------------- 客户端（只读）
    @staticmethod
    async def client_list(limit: int = 6) -> typing.List[typing.Dict[str, typing.Any]]:
        """进行中的团购（未过结束时间），带商品名称 / 图片 / 售价"""
        stmt = (
            select(
                *list(GroupRule.get_table_columns()),
                Goods.name.label("goods_name"),
                Goods.image.label("goods_image"),
                Goods.retail_price.label("goods_price"),
                Goods.brief.label("goods_brief"),
            )
            .outerjoin(Goods, Goods.id == GroupRule.goods_id)
            .where(GroupRule.enabled_flag.is_(True), GroupRule.end_time > datetime.now())
            .order_by(GroupRule.id.desc())
            .limit(limit)
        )
        rows = await GroupRule.get_result(stmt) or []
        for row in rows:
            row["discount"] = float(row["discount"] or 0)
            row["goods_price"] = float(row["goods_price"] or 0)
            row["people"] = int(row["people"] or 1)
        return rows

    @staticmethod
    async def export(params: GroupRuleQuery) -> tuple[bytes, str]:
        rows = await GroupRule.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "团购规则"

        header_fill = PatternFill("solid", fgColor="F2F5F8")
        header_font = Font(bold=True, color="333333")
        center = Alignment(horizontal="center", vertical="center")

        sheet.append(EXPORT_HEADERS)
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center

        for row in rows:
            row = GroupRuleService._decorate(dict(row))
            sheet.append(
                [
                    row.get("id"),
                    row.get("goods_id"),
                    row.get("goods_sn") or "",
                    row.get("goods_name") or "",
                    row.get("discount"),
                    row.get("people"),
                    row.get("status_text"),
                    row.get("end_time") or "",
                ]
            )

        widths = [14, 12, 18, 28, 14, 16, 12, 22]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"团购规则_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
