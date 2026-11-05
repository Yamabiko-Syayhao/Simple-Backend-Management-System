# -*- coding: utf-8 -*-
"""专题及专题商品关联数据层"""

import typing

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, select
from sqlalchemy.dialects.mysql import LONGTEXT

from app.models.base import Base


class Topic(Base):
    """专题主表 mal_topic"""

    __tablename__ = "mal_topic"
    __table_args__ = {"mysql_charset": "utf8mb4"}

    title = Column(String(128), nullable=False, comment="专题标题", index=True)
    subtitle = Column(String(500), nullable=False, comment="专题子标题")
    image = Column(String(1000), nullable=True, comment="专题封面图片 URL")
    content = Column(Text().with_variant(LONGTEXT(), "mysql"), nullable=False, comment="专题富文本 HTML")
    price = Column(Numeric(12, 2), nullable=False, default=0, comment="商品低价")
    read_count = Column(BigInteger, nullable=False, default=0, comment="阅读数量")

    @classmethod
    def _build_stmt(cls, params):
        q = [cls.enabled_flag.is_(True)]
        if getattr(params, "title", None):
            q.append(cls.title.like("%{}%".format(params.title)))
        if getattr(params, "subtitle", None):
            q.append(cls.subtitle.like("%{}%".format(params.subtitle)))
        sort_by = getattr(params, "sort_by", None) or "time"
        column = {"id": cls.id, "time": cls.creation_date, "price": cls.price}[sort_by]
        direction = getattr(params, "sort_order", None) or ("desc" if sort_by == "time" else "asc")
        orders = [column.asc(), cls.id.asc()] if direction == "asc" else [column.desc(), cls.id.desc()]
        return (
            select(cls.get_table_columns(exclude={"content"}))
            .where(*q)
            .order_by(*orders)
        )

    @classmethod
    async def get_list(cls, params) -> typing.Dict[str, typing.Any]:
        # 沿用 Base 分页实现，并使用契约默认值（省略 pageSize 时仍为 20）。
        return await cls.parse_pagination(cls._build_stmt(params), page=params.page, page_size=params.pageSize)

    @classmethod
    async def get_all_by_query(cls, params) -> typing.List[typing.Dict[str, typing.Any]]:
        return await cls.get_result(cls._build_stmt(params)) or []


class TopicGoods(Base):
    """专题商品关联表；关联现有商品，不复制或创建商品"""

    __tablename__ = "mal_topic_goods"
    __table_args__ = (UniqueConstraint("topic_id", "goods_id", name="uq_topic_goods"),)

    topic_id = Column(BigInteger, ForeignKey("mal_topic.id", ondelete="CASCADE"), nullable=False, index=True)
    goods_id = Column(BigInteger, ForeignKey("mal_goods.id", ondelete="CASCADE"), nullable=False, index=True)
    sort = Column(Integer, nullable=False, default=0, comment="专题内商品展示顺序")
