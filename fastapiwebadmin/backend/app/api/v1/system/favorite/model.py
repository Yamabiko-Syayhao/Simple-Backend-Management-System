# -*- coding: utf-8 -*-
"""会员收藏数据层"""

import typing

from sqlalchemy import BigInteger, Column, select

from app.models.base import Base


class Favorite(Base):
    """会员收藏表 mal_favorite"""

    __tablename__ = "mal_favorite"

    member_id = Column(BigInteger, nullable=False, comment="用户ID（mal_member.id）", index=True)
    goods_id = Column(BigInteger, nullable=False, comment="商品ID", index=True)

    @classmethod
    async def get_member_list(cls, params, member_id: int):
        from app.api.v1.system.goods.model import Goods

        stmt = select(cls.id, cls.goods_id, cls.creation_date, Goods.name, Goods.image, Goods.brief,
                      Goods.retail_price, Goods.enabled_flag.label("goods_enabled"), Goods.is_on_sale).outerjoin(
            Goods, Goods.id == cls.goods_id).where(cls.member_id == member_id, cls.enabled_flag.is_(True)).order_by(cls.id.desc())
        return await cls.parse_pagination(stmt, page=params.page, page_size=params.pageSize)

    @classmethod
    async def get_list(cls, params) -> typing.Dict[str, typing.Any]:
        stmt = cls._build_stmt(params)
        return await cls.pagination(stmt)

    @classmethod
    async def get_all_by_query(cls, params) -> typing.List[typing.Dict[str, typing.Any]]:
        stmt = cls._build_stmt(params)
        return await cls.get_result(stmt) or []

    @classmethod
    def _build_stmt(cls, params):
        q = [cls.enabled_flag.is_(True)]
        if getattr(params, "member_id", None):
            q.append(cls.member_id == params.member_id)
        if getattr(params, "goods_id", None):
            q.append(cls.goods_id == params.goods_id)
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.id.asc() if getattr(params, "sort_order", None) == "asc" else cls.id.desc())
        )
