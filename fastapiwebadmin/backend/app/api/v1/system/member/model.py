# -*- coding: utf-8 -*-
"""会员（商城 C 端用户）数据层"""

import typing

from sqlalchemy import Column, Date, Integer, String, Text, select

from app.models.base import Base


class Member(Base):
    """商城会员表 mal_member"""

    __tablename__ = "mal_member"

    username = Column(String(64), nullable=False, comment="登录账号", index=True)
    password = Column(String(128), nullable=False, comment="登录密码（bcrypt）")
    nickname = Column(String(64), nullable=True, comment="用户昵称")
    avatar = Column(Text, nullable=True, comment="用户头像")
    mobile = Column(String(20), nullable=True, comment="手机号码", index=True)
    gender = Column(Integer, nullable=False, default=0, comment="性别 0未知 1男 2女")
    birthday = Column(Date, nullable=True, comment="生日")
    level = Column(Integer, nullable=False, default=0, comment="用户等级 0普通用户 1高级VIP用户")
    status = Column(Integer, nullable=False, default=1, comment="状态 1可用 2禁用 0注销")

    @classmethod
    async def get_list(cls, params) -> typing.Dict[str, typing.Any]:
        """分页查询会员列表（page / pageSize 由 Base.parse_pagination 从 body 读取）"""
        stmt = cls._build_stmt(params)
        return await cls.pagination(stmt)

    @classmethod
    async def get_all_by_query(cls, params) -> typing.List[typing.Dict[str, typing.Any]]:
        """按同样的筛选条件取出全部数据（导出用，不分页）"""
        stmt = cls._build_stmt(params)
        return await cls.get_result(stmt) or []

    @classmethod
    def _build_stmt(cls, params):
        q = [cls.enabled_flag.is_(True)]
        if getattr(params, "username", None):
            q.append(cls.username.like("%{}%".format(params.username)))
        if getattr(params, "nickname", None):
            q.append(cls.nickname.like("%{}%".format(params.nickname)))
        if getattr(params, "mobile", None):
            q.append(cls.mobile.like("%{}%".format(params.mobile)))
        if getattr(params, "member_id", None):
            q.append(cls.id == params.member_id)
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.id.asc() if getattr(params, "sort_order", None) == "asc" else cls.id.desc())
        )

    @classmethod
    async def get_by_username(cls, username: str):
        if not username:
            return None
        stmt = select(cls.get_table_columns()).where(
            cls.username == username, cls.enabled_flag.is_(True)
        )
        return await cls.get_result(stmt, first=True)

    @classmethod
    async def get_by_mobile(cls, mobile: str):
        if not mobile:
            return None
        stmt = select(cls.get_table_columns()).where(
            cls.mobile == mobile, cls.enabled_flag.is_(True)
        )
        return await cls.get_result(stmt, first=True)
