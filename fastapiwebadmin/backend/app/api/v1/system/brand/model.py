# -*- coding: utf-8 -*-
"""品牌制造商数据层"""

import typing

from sqlalchemy import Column, Numeric, String, Text, select

from app.models.base import Base


class Brand(Base):
    """品牌制造商表 mal_brand"""

    __tablename__ = "mal_brand"

    name = Column(String(128), nullable=False, comment="品牌商名称", index=True)
    image = Column(Text, nullable=True, comment="品牌商图片 URL")
    description = Column(Text, nullable=True, comment="介绍")
    floor_price = Column(Numeric(10, 2), nullable=True, comment="底价")

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
        if getattr(params, "brand_id", None):
            q.append(cls.id == params.brand_id)
        if getattr(params, "name", None):
            q.append(cls.name.like("%{}%".format(params.name)))
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.id.asc() if getattr(params, "sort_order", None) == "asc" else cls.id.desc())
        )
