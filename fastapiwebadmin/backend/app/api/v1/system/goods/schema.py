"""商品接口契约。"""
from decimal import Decimal
from typing import Optional
from pydantic import Field, field_validator
from app.shared.schemas.base import BaseSchema


class GoodsSchema(BaseSchema):
    # 商品的可选文本保留空串，不沿用公共层的空串转 None。
    @field_validator("*", mode="before")
    @classmethod
    def blank_strings(cls, value):
        return value


class GoodsQuery(GoodsSchema):
    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=20, ge=1, le=1000)
    goods_id: Optional[int] = None
    goods_sn: Optional[str] = None
    name: Optional[str] = None
    sort_order: Optional[str] = None


class GoodsIn(GoodsSchema):
    id: Optional[int] = None
    name: str = Field(default="", max_length=128)
    goods_sn: Optional[str] = Field(default=None, max_length=64)
    market_price: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    retail_price: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    is_new: bool = False
    is_hot: bool = False
    is_on_sale: bool = False
    image: str = ""
    share_image: str = ""
    gallery: list[str] = Field(default_factory=list)
    unit: str = Field(default="件", max_length=32)
    keywords: list[str] = Field(default_factory=list)
    category_id: int = 0
    brand_id: int = 0
    brief: str = Field(default="", max_length=500)
    detail: str = ""


class GoodsDel(BaseSchema):
    id: int = Field(gt=0)


class GoodsBatchDel(BaseSchema):
    ids: list[int] = Field(min_length=1, max_length=1000)


class GoodsChildIn(GoodsSchema):
    id: Optional[int] = None
    goods_id: int = Field(gt=0)
    name: str = Field(default="", max_length=128)
    value: str = Field(default="", max_length=1000)
    image: str = ""
    price: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    quantity: int = Field(default=0, ge=0, le=2147483647)


class GoodsChildDel(GoodsDel):
    goods_id: int = Field(gt=0)


class GoodsClientQuery(GoodsSchema):
    """客户端商品列表 / 搜索"""

    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1, le=100)
    keyword: Optional[str] = None
    scene: Optional[str] = "default"  # default / new / hot
    brand_id: Optional[int] = None
    category_id: Optional[int] = Field(default=None, gt=0)
