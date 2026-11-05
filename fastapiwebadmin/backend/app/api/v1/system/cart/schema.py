# -*- coding: utf-8 -*-
"""购物车请求契约；会员身份仅从服务端会话读取。"""

from pydantic import ConfigDict, Field, StrictBool

from app.shared.schemas.base import BaseSchema


class CartSchema(BaseSchema):
    # 禁止客户端附带 member_id、price 等可伪造字段。
    model_config = ConfigDict(extra="forbid")


class CartQuery(CartSchema):
    """购物车整车返回，便于全选和合计，当前不拆分页。"""


class CartIn(CartSchema):
    goods_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1, le=999, strict=True)


class CartUpdate(CartSchema):
    id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=999, strict=True)


class CartDel(CartSchema):
    ids: list[int] = Field(min_length=1, max_length=1000)


class CartChecked(CartDel):
    checked: StrictBool
