# -*- coding: utf-8 -*-
"""通用问题（FAQ）数据层"""

import typing

from sqlalchemy import Column, String, Text, select

from app.models.base import Base


class Faq(Base):
    """常见问题表 mal_faq

    后台维护，客户端只读展示（一问一答）。
    """

    __tablename__ = "mal_faq"

    question = Column(String(500), nullable=False, comment="问题内容", index=True)
    answer = Column(Text, nullable=True, comment="问题回复")

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
        if getattr(params, "question", None):
            q.append(cls.question.like("%{}%".format(params.question)))
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.id.asc() if getattr(params, "sort_order", None) == "asc" else cls.id.desc())
        )
