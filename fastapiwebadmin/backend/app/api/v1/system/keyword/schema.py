# -*- coding: utf-8 -*-
"""搜索关键词 Pydantic 契约层"""

from typing import Optional

from pydantic import BaseModel

from app.shared.schemas.base import BaseSchema


class KeywordQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 20
    keyword: Optional[str] = None
    link: Optional[str] = None
    sort_order: Optional[str] = None


class KeywordIn(BaseSchema):
    """新增 / 编辑"""

    id: Optional[int] = None
    keyword: Optional[str] = None
    link: Optional[str] = None
    is_recommend: Optional[int] = 0
    is_default: Optional[int] = 0


class KeywordDel(BaseModel):
    """删除 / 详情"""

    id: int
