# -*- coding: utf-8 -*-
"""团购活动 Pydantic 契约层"""

from typing import Optional

from app.shared.schemas.base import BaseSchema


class GroupActivityQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 20
    rule_id: Optional[int] = None
