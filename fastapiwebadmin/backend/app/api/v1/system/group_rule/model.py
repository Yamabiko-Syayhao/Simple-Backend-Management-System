# -*- coding: utf-8 -*-
"""团购规则数据层"""

import typing

from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, or_, select

from app.api.v1.system.goods.model import Goods
from app.models.base import Base


class GroupRule(Base):
    """团购规则表 mal_group_rule

    一条规则绑定一个商品：满 N 人成团、享受团购价，到期自动下线。
    后台维护，客户端商品详情页读取后展示"去拼团"。
    """

    __tablename__ = "mal_group_rule"

    goods_id = Column(BigInteger, nullable=False, comment="商品ID", index=True)
    discount = Column(Numeric(12, 2), nullable=False, default=0, comment="团购优惠（团购折扣）")
    people = Column(Integer, nullable=False, default=2, comment="团购人数要求")
    end_time = Column(DateTime, nullable=False, comment="过期时间", index=True)

    @classmethod
    async def get_list(cls, params) -> typing.Dict[str, typing.Any]:
        return await cls.pagination(cls._build_stmt(params))

    @classmethod
    async def get_all_by_query(cls, params) -> typing.List[typing.Dict[str, typing.Any]]:
        return await cls.get_result(cls._build_stmt(params)) or []

    @classmethod
    def _build_stmt(cls, params):
        q = [cls.enabled_flag.is_(True)]
        keyword = (getattr(params, "keyword", None) or "").strip()
        if keyword:
            conditions = [
                Goods.goods_sn.like("%{}%".format(keyword)),
                Goods.name.like("%{}%".format(keyword)),
            ]
            if keyword.isdigit():
                conditions.append(cls.goods_id == int(keyword))
            q.append(or_(*conditions))
        return (
            select(
                *list(cls.get_table_columns()),
                Goods.name.label("goods_name"),
                Goods.image.label("goods_image"),
                Goods.goods_sn.label("goods_sn"),
            )
            .outerjoin(Goods, Goods.id == cls.goods_id)
            .where(*q)
            .order_by(cls.id.desc())
        )
