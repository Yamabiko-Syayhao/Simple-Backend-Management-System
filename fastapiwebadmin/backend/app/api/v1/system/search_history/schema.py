# -*- coding: utf-8 -*-
"""会员搜索历史 Pydantic 契约层"""

from typing import Optional

from pydantic import BaseModel

from app.shared.schemas.base import BaseSchema


class SearchHistoryQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 20
    member_id: Optional[int] = None
    keyword: Optional[str] = None
    # 服务端排序：asc / desc（默认 desc），由前端表头排序触发
    sort_order: Optional[str] = None


class SearchHistoryIn(BaseSchema):
    """新增 / 编辑搜索历史"""

    id: Optional[int] = None
    member_id: Optional[int] = None
    keyword: Optional[str] = None


class SearchHistoryDel(BaseModel):
    """删除 / 详情"""

    id: int


class SearchHistoryKeywordIn(BaseSchema):
    """客户端：记录一次搜索"""

    keyword: Optional[str] = None
