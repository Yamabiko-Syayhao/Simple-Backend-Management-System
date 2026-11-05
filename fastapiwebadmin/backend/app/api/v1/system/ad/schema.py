# -*- coding: utf-8 -*-
"""广告管理 Pydantic 契约层"""

from typing import Literal, Optional

from pydantic import Field

from app.shared.schemas.base import BaseSchema


class AdQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=20, ge=1, le=1000)
    title: Optional[str] = None
    content: Optional[str] = None
    sort_order: Optional[Literal["asc", "desc"]] = None


class AdIn(BaseSchema):
    """新增 / 编辑广告"""

    id: Optional[int] = Field(default=None, gt=0)
    title: Optional[str] = Field(default=None, max_length=128)
    content: Optional[str] = Field(default=None, max_length=1000)
    image: Optional[str] = Field(default=None, max_length=1000)
    position: Literal[1] = 1
    link: Optional[str] = Field(default=None, max_length=1000)
    status: Literal[0, 1] = 1


class AdDel(BaseSchema):
    """删除 / 详情"""

    id: int = Field(gt=0)


class AdBannerQuery(BaseSchema):
    """客户端轮播查询，当前仅支持首页"""

    position: Literal[1] = 1
