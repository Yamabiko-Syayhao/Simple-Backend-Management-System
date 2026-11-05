# -*- coding: utf-8 -*-
"""通用问题 Pydantic 契约层"""

from typing import Optional

from pydantic import BaseModel

from app.shared.schemas.base import BaseSchema


class FaqQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 20
    question: Optional[str] = None
    sort_order: Optional[str] = None


class FaqIn(BaseSchema):
    """新增 / 编辑"""

    id: Optional[int] = None
    question: Optional[str] = None
    answer: Optional[str] = None


class FaqDel(BaseModel):
    """删除 / 详情"""

    id: int
