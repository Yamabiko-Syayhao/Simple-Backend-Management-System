# -*- coding: utf-8 -*-
"""团购规则 Pydantic 契约层"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.shared.schemas.base import BaseSchema


class GroupRuleQuery(BaseSchema):
    """列表 / 导出查询条件：keyword 支持商品编号、商品名称、商品ID"""

    page: int = 1
    pageSize: int = 20
    keyword: Optional[str] = None


class GroupRuleIn(BaseSchema):
    """新增 / 编辑"""

    id: Optional[int] = None
    goods_id: Optional[int] = Field(default=None, gt=0)
    discount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    people: int = Field(default=2, ge=1, le=9999)
    end_time: Optional[datetime] = None


class GroupRuleDel(BaseModel):
    """删除 / 详情"""

    id: int
