# -*- coding: utf-8 -*-
"""商品评论 Pydantic 契约层"""

from typing import Optional

from pydantic import BaseModel

from app.shared.schemas.base import BaseSchema


class GoodsCommentQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 20
    member_id: Optional[int] = None
    goods_id: Optional[int] = None


class GoodsCommentReplyIn(BaseSchema):
    """回复评论"""

    comment_id: Optional[int] = None
    content: Optional[str] = None


class GoodsCommentDel(BaseModel):
    """删除"""

    id: int
