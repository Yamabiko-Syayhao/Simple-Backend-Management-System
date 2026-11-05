# -*- coding: utf-8 -*-
"""专题管理 Pydantic 契约层"""

from decimal import Decimal, DecimalException
from typing import Literal, Optional

from pydantic import Field, PositiveInt, field_validator

from app.shared.schemas.base import BaseSchema


class TopicQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=20, ge=1, le=1000)
    title: Optional[str] = None
    subtitle: Optional[str] = None
    sort_by: Literal["id", "time", "price"] = "time"
    sort_order: Optional[Literal["asc", "desc"]] = None


class TopicIn(BaseSchema):
    """专题创建 / 编辑与关联商品一次保存"""

    id: Optional[int] = Field(default=None, gt=0)
    title: Optional[str] = Field(default=None, max_length=128)
    subtitle: Optional[str] = Field(default=None, max_length=500)
    image: Optional[str] = Field(default=None, max_length=1000)
    content: Optional[str] = None
    price: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    read_count: int = Field(default=0, ge=0, le=9007199254740991)
    goods_ids: list[PositiveInt] = Field(default_factory=list, max_length=1000)

    @field_validator("read_count", mode="before")
    @classmethod
    def parse_read_count(cls, value):
        if isinstance(value, str) and value.strip().lower().endswith("k"):
            try:
                count = Decimal(value.strip()[:-1]) * 1000
                if not count.is_finite() or count != count.to_integral_value() or not 0 <= count <= 9007199254740991:
                    raise ValueError("阅读量必须为整数")
                return int(count)
            except DecimalException:
                raise ValueError("阅读量格式不正确")
        return value


class TopicDel(BaseSchema):
    """详情 / 删除"""

    id: int = Field(gt=0)


class TopicBatchDel(BaseSchema):
    """批量删除，空选由业务层返回明确提示"""

    ids: list[PositiveInt] = Field(default_factory=list, max_length=1000)
