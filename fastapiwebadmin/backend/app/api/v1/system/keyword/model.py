# -*- coding: utf-8 -*-
"""搜索关键词数据层"""

import typing

from sqlalchemy import Column, Integer, String, select

from app.models.base import Base


class Keyword(Base):
    """搜索关键词表 mal_keyword

    用于客户端搜索框下方的热门/推荐词，后台维护。
    """

    __tablename__ = "mal_keyword"

    keyword = Column(String(64), nullable=False, comment="关键词", index=True)
    link = Column(String(500), nullable=True, comment="跳转链接")
    is_recommend = Column(Integer, nullable=False, default=0, comment="是否推荐 1推荐 0普通")
    is_default = Column(Integer, nullable=False, default=0, comment="是否默认 1默认 0非默认")

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
        if getattr(params, "keyword", None):
            q.append(cls.keyword.like("%{}%".format(params.keyword)))
        if getattr(params, "link", None):
            q.append(cls.link.like("%{}%".format(params.link)))
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.id.asc() if getattr(params, "sort_order", None) == "asc" else cls.id.desc())
        )
