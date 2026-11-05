# -*- coding: utf-8 -*-
"""统计报表请求契约。"""

from typing import Optional

from pydantic import ConfigDict, Field

from app.shared.schemas.base import BaseSchema


class StatisticQuery(BaseSchema):
    """商城总量统计不接受客户端指定会员、价格或筛选条件。"""

    model_config = ConfigDict(extra="forbid")


class StatisticChartQuery(BaseSchema):
    """图表区间：days=0 表示全部历史，>0 表示最近 N 天（含今天）。"""

    days: Optional[int] = Field(default=0, ge=0, le=3650)
