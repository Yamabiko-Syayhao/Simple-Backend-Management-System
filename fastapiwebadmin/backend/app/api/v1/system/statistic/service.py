# -*- coding: utf-8 -*-
"""统计报表业务层。"""

import typing

from app.api.v1.system.statistic.model import Statistic


def _series(rows: typing.List[typing.Dict[str, typing.Any]], field: str) -> typing.List[typing.Any]:
    return [row.get(field) for row in rows]


class StatisticService:
    @staticmethod
    async def count_statistic() -> typing.Dict[str, int]:
        return await Statistic.get_counts()

    @staticmethod
    async def user_chart(days: int = 0) -> typing.Dict[str, typing.Any]:
        rows = await Statistic.user_daily(days)
        return {
            "dates": _series(rows, "date"),
            "rows": rows,
            "series": {"user_count": _series(rows, "user_count")},
        }

    @staticmethod
    async def order_chart(days: int = 0) -> typing.Dict[str, typing.Any]:
        rows = await Statistic.order_daily(days)
        for row in rows:
            # 客单价 = 当天订单总额 / 当天订单量，保留两位
            row["avg_amount"] = round(row["order_amount"] / row["order_count"], 2) if row["order_count"] else 0
        return {
            "dates": _series(rows, "date"),
            "rows": rows,
            "series": {
                "order_count": _series(rows, "order_count"),
                "buyer_count": _series(rows, "buyer_count"),
                "order_amount": _series(rows, "order_amount"),
                "avg_amount": _series(rows, "avg_amount"),
            },
        }

    @staticmethod
    async def goods_chart(days: int = 0) -> typing.Dict[str, typing.Any]:
        rows = await Statistic.goods_daily(days)
        return {
            "dates": _series(rows, "date"),
            "rows": rows,
            "series": {
                "order_count": _series(rows, "order_count"),
                "goods_quantity": _series(rows, "goods_quantity"),
                "goods_amount": _series(rows, "goods_amount"),
            },
        }
