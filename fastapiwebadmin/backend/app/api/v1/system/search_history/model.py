# -*- coding: utf-8 -*-
"""会员搜索历史数据层"""

import typing

from sqlalchemy import BigInteger, Column, String, select

from app.models.base import Base


class SearchHistory(Base):
    """会员搜索历史表 mal_search_history"""

    __tablename__ = "mal_search_history"

    member_id = Column(BigInteger, nullable=False, comment="用户ID（mal_member.id）", index=True)
    keyword = Column(String(255), nullable=True, comment="搜索关键字", index=True)

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
        if getattr(params, "keyword", None):
            q.append(cls.keyword.like("%{}%".format(params.keyword)))
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.id.asc() if getattr(params, "sort_order", None) == "asc" else cls.id.desc())
        )

    @classmethod
    def my_stmt(cls, member_id: int, limit: int = 20):
        """客户端：当前会员最近的搜索记录"""
        return (
            select(cls.get_table_columns())
            .where(cls.member_id == member_id, cls.enabled_flag.is_(True))
            .order_by(cls.id.desc())
            .limit(limit)
        )
