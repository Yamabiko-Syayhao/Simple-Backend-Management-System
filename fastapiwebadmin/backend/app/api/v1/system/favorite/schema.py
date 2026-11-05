# -*- coding: utf-8 -*-
"""会员收藏 Pydantic 契约层"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.shared.schemas.base import BaseSchema


class FavoriteQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 10
    member_id: Optional[int] = None
    goods_id: Optional[int] = None
    # 服务端排序：asc / desc（默认 desc），由前端表头排序触发
    sort_order: Optional[str] = None


class FavoriteIn(BaseSchema):
    """新增 / 编辑收藏"""

    id: Optional[int] = None
    member_id: Optional[int] = None
    goods_id: Optional[int] = None


class FavoriteDel(BaseModel):
    """删除 / 详情"""

    id: int


class FavoriteMineQuery(BaseSchema):
    model_config = ConfigDict(extra="forbid")
    page: int = Field(default=1, ge=1, strict=True)
    pageSize: int = Field(default=20, ge=1, le=100, strict=True)


class FavoriteMineDel(BaseSchema):
    model_config = ConfigDict(extra="forbid")
    id: int = Field(gt=0, strict=True)


class FavoriteMineSet(BaseSchema):
    model_config = ConfigDict(extra="forbid")
    goods_id: int = Field(gt=0, strict=True)
    collected: bool = Field(strict=True)
