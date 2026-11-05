# -*- coding: utf-8 -*-
"""品牌制造商 Pydantic 契约层"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.shared.schemas.base import BaseSchema


class BrandQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 20
    brand_id: Optional[int] = None
    name: Optional[str] = None
    sort_order: Optional[str] = None


class BrandIn(BaseSchema):
    """新增 / 编辑品牌商"""

    id: Optional[int] = None
    name: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    floor_price: Optional[Decimal] = None


class BrandDel(BaseModel):
    """删除 / 详情"""

    id: int
