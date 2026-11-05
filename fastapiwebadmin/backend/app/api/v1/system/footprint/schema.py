# -*- coding: utf-8 -*-
"""会员足迹 Pydantic 契约层"""

from typing import Optional

from pydantic import BaseModel

from app.shared.schemas.base import BaseSchema


class FootprintQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 20
    member_id: Optional[int] = None
    goods_id: Optional[int] = None
    # 服务端排序：asc / desc（默认 desc），由前端表头排序触发
    sort_order: Optional[str] = None


class FootprintIn(BaseSchema):
    """新增 / 编辑足迹"""

    id: Optional[int] = None
    member_id: Optional[int] = None
    goods_id: Optional[int] = None


class FootprintDel(BaseModel):
    """删除 / 详情"""

    id: int
