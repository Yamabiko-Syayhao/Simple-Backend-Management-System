# -*- coding: utf-8 -*-
"""商品类目 Pydantic 契约层"""

from typing import Optional

from pydantic import BaseModel

from app.shared.schemas.base import BaseSchema


class CategoryIn(BaseSchema):
    """新增 / 编辑类目"""

    id: Optional[int] = None
    name: Optional[str] = None
    keywords: Optional[str] = None
    level: Optional[int] = 1
    parent_id: Optional[int] = 0
    icon: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None


class CategoryDel(BaseModel):
    """删除 / 详情"""

    id: int
