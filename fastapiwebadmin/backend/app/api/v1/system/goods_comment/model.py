# -*- coding: utf-8 -*-
"""商品评论数据层"""

import typing

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text, select

from app.models.base import Base


class GoodsComment(Base):
    """商品评论表 mal_goods_comment

    数据来源：客户端（会员）对已购买商品发表评价；后台只做查看、回复、删除。
    """

    __tablename__ = "mal_goods_comment"

    member_id = Column(BigInteger, nullable=True, comment="用户ID", index=True)
    username = Column(String(64), nullable=True, comment="用户昵称")
    goods_id = Column(BigInteger, nullable=False, comment="商品ID", index=True)
    score = Column(Integer, nullable=False, default=5, comment="打分 1-5")
    content = Column(Text, nullable=True, comment="评论内容")
    images = Column(Text, nullable=True, comment="评论图片，多张用英文逗号分隔")
    comment_time = Column(DateTime, nullable=True, comment="评论时间", index=True)
    reply_content = Column(Text, nullable=True, comment="商家回复内容")
    reply_time = Column(DateTime, nullable=True, comment="回复时间")

    @classmethod
    async def get_list(cls, params) -> typing.Dict[str, typing.Any]:
        return await cls.pagination(cls._build_stmt(params))

    @classmethod
    async def get_all_by_query(cls, params) -> typing.List[typing.Dict[str, typing.Any]]:
        return await cls.get_result(cls._build_stmt(params)) or []

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
            .order_by(cls.comment_time.desc(), cls.id.desc())
        )
