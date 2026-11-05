# -*- coding: utf-8 -*-
"""团购活动数据层"""

import typing

from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, String, select

from app.models.base import Base


class GroupActivity(Base):
    """团购活动表 mal_group_activity

    客户端用户对某条团购规则开团后生成一条活动记录（发起人 + 订单），
    其他用户参团时写入 mal_group_activity_member。
    """

    __tablename__ = "mal_group_activity"

    rule_id = Column(BigInteger, nullable=False, comment="团购规则ID", index=True)
    order_id = Column(BigInteger, nullable=True, comment="发起人订单ID")
    member_id = Column(BigInteger, nullable=True, comment="发起人用户ID")
    participants = Column(Integer, nullable=False, default=0, comment="参与人数")
    discount = Column(Numeric(12, 2), nullable=False, default=0, comment="团购折扣")
    people = Column(Integer, nullable=False, default=1, comment="团购要求")
    share_image = Column(String(500), nullable=True, comment="分享图片")
    start_time = Column(DateTime, nullable=True, comment="开始时间", index=True)
    end_time = Column(DateTime, nullable=True, comment="结束时间")

    @classmethod
    async def get_list(cls, params) -> typing.Dict[str, typing.Any]:
        return await cls.pagination(cls._build_stmt(params))

    @classmethod
    async def get_all_by_query(cls, params) -> typing.List[typing.Dict[str, typing.Any]]:
        return await cls.get_result(cls._build_stmt(params)) or []

    @classmethod
    def _build_stmt(cls, params):
        q = [cls.enabled_flag.is_(True)]
        if getattr(params, "rule_id", None):
            q.append(cls.rule_id == params.rule_id)
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.start_time.desc(), cls.id.desc())
        )


class GroupActivityMember(Base):
    """团购活动参与记录表 mal_group_activity_member"""

    __tablename__ = "mal_group_activity_member"

    activity_id = Column(BigInteger, nullable=False, comment="团购活动ID", index=True)
    order_id = Column(BigInteger, nullable=True, comment="订单ID")
    member_id = Column(BigInteger, nullable=True, comment="用户ID")
    join_time = Column(DateTime, nullable=True, comment="参与时间")

    @classmethod
    async def get_by_activity_ids(cls, activity_ids: typing.List[int]) -> typing.List[typing.Dict[str, typing.Any]]:
        if not activity_ids:
            return []
        stmt = (
            select(cls.get_table_columns())
            .where(cls.activity_id.in_(activity_ids), cls.enabled_flag.is_(True))
            .order_by(cls.join_time.asc(), cls.id.asc())
        )
        return await cls.get_result(stmt) or []
