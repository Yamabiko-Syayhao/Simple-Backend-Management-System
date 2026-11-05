# -*- coding: utf-8 -*-
"""会员意见反馈数据层"""

import typing

from sqlalchemy import BigInteger, Column, String, Text, select

from app.models.base import Base


class Feedback(Base):
    """会员意见反馈表 mal_feedback"""

    __tablename__ = "mal_feedback"

    member_id = Column(BigInteger, nullable=True, comment="用户ID（mal_member.id）", index=True)
    username = Column(String(64), nullable=True, comment="用户名（提交时快照）", index=True)
    mobile = Column(String(20), nullable=True, comment="手机号码（提交时快照）")
    feedback_type = Column(String(32), nullable=True, comment="反馈类型，如：功能建议 / 商品问题 / 其他")
    content = Column(Text, nullable=True, comment="反馈内容")
    images = Column(Text, nullable=True, comment="反馈图片 URL，多个用英文逗号分隔")

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
        if getattr(params, "feedback_id", None):
            q.append(cls.id == params.feedback_id)
        if getattr(params, "username", None):
            q.append(cls.username.like("%{}%".format(params.username)))
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.id.asc() if getattr(params, "sort_order", None) == "asc" else cls.id.desc())
        )
