# -*- coding: utf-8 -*-
"""会员模块 Pydantic 契约层"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, field_validator

from app.shared.schemas.base import BaseSchema


class MemberQuery(BaseSchema):
    """会员列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 20
    member_id: Optional[int] = None
    username: Optional[str] = None
    nickname: Optional[str] = None
    mobile: Optional[str] = None
    # 服务端排序：asc / desc（默认 desc），由前端表头排序触发
    sort_order: Optional[str] = None


class MemberIn(BaseSchema):
    """新增 / 编辑会员"""

    id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    mobile: Optional[str] = None
    gender: Optional[int] = 0
    birthday: Optional[date] = None
    level: Optional[int] = 0
    status: Optional[int] = 1


class MemberDel(BaseModel):
    """删除 / 详情"""

    id: int


class MemberLoginIn(BaseSchema):
    """会员登录"""

    username: str
    password: str


class MemberRegisterIn(BaseSchema):
    """会员注册"""

    username: str
    password: str
    nickname: Optional[str] = None
    mobile: Optional[str] = None


class MemberProfileIn(BaseSchema):
    """本人信息按字段更新，头像只能走专用上传接口。"""

    model_config = ConfigDict(extra="forbid")

    nickname: Optional[StrictStr] = Field(default=None, min_length=1, max_length=64)
    gender: Optional[StrictInt] = Field(default=None, ge=0, le=2)

    @field_validator("nickname", mode="before")
    @classmethod
    def strip_nickname(cls, value):
        return value.strip() if isinstance(value, str) else value


class MemberMobileIn(BaseSchema):
    """手机号不是登录账号，仅在校验本人当前密码后更新。"""

    model_config = ConfigDict(extra="forbid")

    password: StrictStr = Field(min_length=1, max_length=72)
    mobile: StrictStr = Field(pattern=r"^1[3-9]\d{9}$")

    @field_validator("mobile", mode="before")
    @classmethod
    def strip_mobile(cls, value):
        return value.strip() if isinstance(value, str) else value
