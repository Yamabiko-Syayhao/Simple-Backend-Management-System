# -*- coding: utf-8 -*-
"""广告管理数据层"""

import typing

from sqlalchemy import Column, Integer, String, Text, select

from app.models.base import Base


class Ad(Base):
    """首页轮播广告表 mal_ad"""

    __tablename__ = "mal_ad"

    title = Column(String(128), nullable=False, comment="广告标题", index=True)
    content = Column(Text, nullable=False, comment="广告内容")
    image = Column(String(1000), nullable=False, comment="广告图片 URL")
    position = Column(Integer, nullable=False, default=1, comment="广告位置：1 首页")
    link = Column(String(1000), nullable=True, comment="活动链接")
    status = Column(Integer, nullable=False, default=1, comment="是否启用：1 启用 / 0 不启用")

    @classmethod
    async def get_list(cls, params) -> typing.Dict[str, typing.Any]:
        return await cls.pagination(cls._build_stmt(params))

    @classmethod
    async def get_all_by_query(cls, params) -> typing.List[typing.Dict[str, typing.Any]]:
        return await cls.get_result(cls._build_stmt(params)) or []

    @classmethod
    def _build_stmt(cls, params):
        q = [cls.enabled_flag.is_(True)]
        if getattr(params, "title", None):
            q.append(cls.title.like("%{}%".format(params.title)))
        if getattr(params, "content", None):
            q.append(cls.content.like("%{}%".format(params.content)))
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.id.asc() if getattr(params, "sort_order", None) == "asc" else cls.id.desc())
        )

    @classmethod
    async def get_banners(cls, position: int) -> typing.List[typing.Dict[str, typing.Any]]:
        """只返回当前启用的广告，供首页轮播读取。"""
        stmt = (
            select(cls.id, cls.title, cls.content, cls.image, cls.position, cls.link)
            .where(cls.enabled_flag.is_(True), cls.status == 1, cls.position == position)
            .order_by(cls.id.asc())
        )
        return await cls.get_result(stmt) or []
