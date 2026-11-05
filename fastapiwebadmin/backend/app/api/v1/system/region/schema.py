# -*- coding: utf-8 -*-
"""行政区域 Pydantic 契约层"""

from typing import Optional

from pydantic import BaseModel


class RegionChildrenIn(BaseModel):
    """查询下级区域"""

    parent_id: Optional[int] = 0
