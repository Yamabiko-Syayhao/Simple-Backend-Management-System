# -*- coding: utf-8 -*-
"""统计报表数据层：聚合现有商城表，不创建统计表。"""

import typing
from datetime import datetime, timedelta

from sqlalchemy import func, select

from app.api.v1.system.goods.model import Goods, GoodsProduct
from app.api.v1.system.member.model import Member
from app.api.v1.system.order.model import Order, OrderItem
from app.database.sqlalchemy import async_session_factory


def _since(days: int) -> typing.Optional[datetime]:
    if not days or days <= 0:
        return None
    now = datetime.now()
    return datetime(now.year, now.month, now.day) - timedelta(days=days - 1)


def _date_text(value) -> str:
    if value is None:
        return ""
    return value.strftime("%Y-%m-%d") if hasattr(value, "strftime") else str(value)


class Statistic:
    @classmethod
    async def get_counts(cls) -> typing.Dict[str, int]:
        models = {"users": Member, "goods": Goods, "products": GoodsProduct, "orders": Order}
        # 一条 SQL 内取得同一读快照，不加载记录明细或把库存件数误当成 SKU 数。
        stmt = select(*[
            select(func.count(model.id)).where(model.enabled_flag.is_(True)).scalar_subquery().label(key)
            for key, model in models.items()
        ])
        async with async_session_factory() as session:
            row = (await session.execute(stmt)).mappings().one()
            return {key: int(row[key] or 0) for key in models}

    # ------------------------------------------------------------------ 折线 / 柱状图数据
    @classmethod
    async def user_daily(cls, days: int = 0) -> typing.List[typing.Dict[str, typing.Any]]:
        """按天统计新增会员数（用户增长数）"""
        day = func.date(Member.creation_date).label("d")
        stmt = (
            select(day, func.count(Member.id).label("cnt"))
            .where(Member.enabled_flag.is_(True))
            .group_by(day)
            .order_by(day)
        )
        since = _since(days)
        if since:
            stmt = stmt.where(Member.creation_date >= since)
        async with async_session_factory() as session:
            rows = (await session.execute(stmt)).all()
        return [{"date": _date_text(row.d), "user_count": int(row.cnt or 0)} for row in rows]

    @classmethod
    async def order_daily(cls, days: int = 0) -> typing.List[typing.Dict[str, typing.Any]]:
        """按天统计订单量、下单用户数、订单总额（客单价由服务层算）"""
        day = func.date(Order.order_time).label("d")
        stmt = (
            select(
                day,
                func.count(Order.id).label("order_count"),
                func.count(func.distinct(Order.member_id)).label("buyer_count"),
                func.coalesce(func.sum(Order.total_amount), 0).label("amount"),
            )
            .where(Order.enabled_flag.is_(True))
            .group_by(day)
            .order_by(day)
        )
        since = _since(days)
        if since:
            stmt = stmt.where(Order.order_time >= since)
        async with async_session_factory() as session:
            rows = (await session.execute(stmt)).all()
        return [
            {
                "date": _date_text(row.d),
                "order_count": int(row.order_count or 0),
                "buyer_count": int(row.buyer_count or 0),
                "order_amount": float(row.amount or 0),
            }
            for row in rows
        ]

    @classmethod
    async def goods_daily(cls, days: int = 0) -> typing.List[typing.Dict[str, typing.Any]]:
        """按天统计下单货品数量与货品总额"""
        day = func.date(Order.order_time).label("d")
        stmt = (
            select(
                day,
                func.count(func.distinct(Order.id)).label("order_count"),
                func.coalesce(func.sum(OrderItem.quantity), 0).label("quantity"),
                func.coalesce(func.sum(OrderItem.price * OrderItem.quantity), 0).label("amount"),
            )
            .select_from(Order)
            .join(OrderItem, OrderItem.order_id == Order.id)
            .where(Order.enabled_flag.is_(True))
            .group_by(day)
            .order_by(day)
        )
        since = _since(days)
        if since:
            stmt = stmt.where(Order.order_time >= since)
        async with async_session_factory() as session:
            rows = (await session.execute(stmt)).all()
        return [
            {
                "date": _date_text(row.d),
                "order_count": int(row.order_count or 0),
                "goods_quantity": int(row.quantity or 0),
                "goods_amount": float(row.amount or 0),
            }
            for row in rows
        ]
