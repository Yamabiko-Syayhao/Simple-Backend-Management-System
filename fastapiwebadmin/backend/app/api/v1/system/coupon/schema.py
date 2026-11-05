# -*- coding: utf-8 -*-
"""优惠券 Pydantic 契约层"""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import ConfigDict, Field, PositiveInt

from app.shared.schemas.base import BaseSchema


class CouponQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=20, ge=1, le=1000)
    name: Optional[str] = None
    type: Optional[Literal[0, 1, 2]] = None
    status: Optional[Literal[0, 1, 2]] = None
    sort_order: Optional[Literal["asc", "desc"]] = None


class CouponIn(BaseSchema):
    """创建 / 编辑优惠券，范围与主记录一起保存"""

    id: Optional[int] = Field(default=None, gt=0)
    name: Optional[str] = Field(default=None, max_length=128)
    description: Optional[str] = Field(default=None, max_length=500)
    tag: Optional[str] = Field(default=None, max_length=128)
    min: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    discount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    limit: int = Field(default=1, ge=1, le=2147483647)
    type: Literal[0, 1, 2] = 0
    total: int = Field(default=0, ge=0, le=2147483647)
    time_type: Literal[0, 1] = 0
    days: int = Field(default=0, ge=0, le=2147483647)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    goods_type: Literal[0, 1, 2] = 0
    category_ids: list[PositiveInt] = Field(default_factory=list, max_length=1000)
    goods_ids: list[PositiveInt] = Field(default_factory=list, max_length=1000)
    status: Literal[0, 1, 2] = 0


class CouponDel(BaseSchema):
    """详情 / 删除"""

    id: int = Field(gt=0)


class CouponUserQuery(BaseSchema):
    """指定优惠券的会员领取/使用记录查询"""

    coupon_id: int = Field(gt=0)
    user_id: Optional[int] = Field(default=None, gt=0)
    status: Optional[Literal[0, 1, 2]] = None
    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=20, ge=1, le=1000)
    sort_order: Optional[Literal["asc", "desc"]] = None


class CouponClaimIn(BaseSchema):
    """会员领券，不接收会员身份或金额。"""

    model_config = ConfigDict(extra="forbid")
    id: int = Field(gt=0, strict=True)


class CouponMineQuery(BaseSchema):
    """会员本人的已领优惠券。"""

    model_config = ConfigDict(extra="forbid")
    status: Optional[Literal[0, 1, 2]] = None
