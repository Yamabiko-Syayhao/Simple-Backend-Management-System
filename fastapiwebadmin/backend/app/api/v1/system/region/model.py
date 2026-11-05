# -*- coding: utf-8 -*-
"""行政区域数据层"""

import typing

from sqlalchemy import BigInteger, Column, Integer, String, select

from app.models.base import Base


class Region(Base):
    """行政区域表 mal_region（省 / 市 / 区 三级，GB/T 2260 编码）"""

    __tablename__ = "mal_region"

    name = Column(String(64), nullable=False, comment="区域名称", index=True)
    code = Column(String(12), nullable=False, comment="行政区域编码", index=True)
    parent_id = Column(BigInteger, nullable=False, default=0, comment="父级ID，省级为 0", index=True)
    level = Column(Integer, nullable=False, default=1, comment="层级 1省 2市 3区")
    sort = Column(Integer, nullable=True, default=0, comment="同级排序")

    @classmethod
    async def get_all(cls) -> typing.List[typing.Dict[str, typing.Any]]:
        stmt = (
            select(cls.get_table_columns())
            .where(cls.enabled_flag.is_(True))
            .order_by(cls.level.asc(), cls.sort.asc(), cls.id.asc())
        )
        return await cls.get_result(stmt) or []

    @classmethod
    async def get_children(cls, parent_id: int) -> typing.List[typing.Dict[str, typing.Any]]:
        stmt = (
            select(cls.get_table_columns())
            .where(cls.parent_id == parent_id, cls.enabled_flag.is_(True))
            .order_by(cls.sort.asc(), cls.id.asc())
        )
        return await cls.get_result(stmt) or []
