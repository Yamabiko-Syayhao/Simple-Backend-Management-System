# -*- coding: utf-8 -*-
"""会员意见反馈 Pydantic 契约层"""

from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.shared.schemas.base import BaseSchema


class FeedbackQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 20
    feedback_id: Optional[int] = None
    username: Optional[str] = None
    sort_order: Optional[str] = None


class FeedbackIn(BaseSchema):
    """新增 / 编辑反馈"""

    id: Optional[int] = None
    member_id: Optional[int] = None
    username: Optional[str] = None
    mobile: Optional[str] = None
    feedback_type: Optional[str] = None
    content: Optional[str] = None
    images: Optional[str] = None


class FeedbackDel(BaseModel):
    """删除 / 详情"""

    id: int


class FeedbackMineIn(BaseSchema):
    """当前会员反馈，身份与用户名仅由服务端取值。"""

    model_config = ConfigDict(extra="forbid")
    feedback_type: Literal["功能建议", "商品问题", "物流问题", "其他"]
    content: str = Field(min_length=1, max_length=2000, strict=True)
    mobile: Optional[str] = Field(default=None, pattern=r"^1[3-9]\d{9}$", strict=True)


class FeedbackContactQuery(BaseSchema):
    model_config = ConfigDict(extra="forbid")
