# -*- coding: utf-8 -*-
"""收货地址数据层"""

import typing

from sqlalchemy import BigInteger, Column, Integer, String, select

from app.models.base import Base


class Address(Base):
    """会员收货地址表 mal_address"""

    __tablename__ = "mal_address"

    member_id = Column(BigInteger, nullable=False, comment="用户ID（mal_member.id）", index=True)
    receiver_name = Column(String(64), nullable=False, comment="收货人名称")
    mobile = Column(String(20), nullable=True, comment="手机号码")
    region = Column(String(255), nullable=True, comment="区域地址（省市区）")
    detail = Column(String(255), nullable=True, comment="详细地址")
    is_default = Column(Integer, nullable=False, default=0, comment="是否默认 1是 0否")

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
        if getattr(params, "receiver_name", None):
            q.append(cls.receiver_name.like("%{}%".format(params.receiver_name)))
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.id.asc() if getattr(params, "sort_order", None) == "asc" else cls.id.desc())
        )

    @classmethod
    def my_stmt(cls, member_id: int):
        return (
            select(cls)
            .where(cls.member_id == member_id, cls.enabled_flag.is_(True))
            .order_by(cls.is_default.desc(), cls.id.asc())
        )
