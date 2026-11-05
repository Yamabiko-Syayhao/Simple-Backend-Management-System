# -*- coding: utf-8 -*-
"""商城订单 Pydantic 契约层"""

from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.shared.schemas.base import BaseSchema


class OrderQuery(BaseSchema):
    """订单列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 20
    username: Optional[str] = None
    receiver_name: Optional[str] = None
    order_no: Optional[str] = None
    status: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class OrderDel(BaseModel):
    """删除 / 详情"""

    id: int


class OrderCollectIn(BaseSchema):
    """订单收款"""

    id: int
    pay_amount: Optional[float] = None


class OrderDeliverIn(BaseSchema):
    """订单发货"""

    id: int
    express_company: Optional[str] = None
    express_no: Optional[str] = None


class OrderRefundIn(BaseSchema):
    """订单退款"""

    id: int
    refund_amount: Optional[float] = None


class CheckoutSchema(BaseSchema):
    model_config = ConfigDict(extra="forbid")


class CheckoutPreview(CheckoutSchema):
    source: Literal["cart", "buy_now"]
    cart_ids: list[int] = Field(default_factory=list, max_length=1000)
    goods_id: Optional[int] = Field(default=None, gt=0)
    product_id: Optional[int] = Field(default=None, gt=0)
    quantity: Optional[int] = Field(default=None, ge=1, le=999, strict=True)
    address_id: Optional[int] = Field(default=None, gt=0)
    coupon_user_id: Optional[int] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def selection(self):
        if self.source == "cart":
            if not self.cart_ids or any(isinstance(i, bool) or i <= 0 for i in self.cart_ids):
                raise ValueError("请选择购物车商品")
            if self.goods_id is not None or self.product_id is not None or self.quantity is not None:
                raise ValueError("购物车结算不接受直接购买参数")
        elif not self.goods_id or not self.product_id or not self.quantity or self.cart_ids:
            raise ValueError("请选择购买商品、规格和数量")
        return self


class CheckoutQuote(CheckoutSchema):
    quote_token: str = Field(pattern=r"^[a-f0-9]{32}$")


class CheckoutSubmit(CheckoutQuote):
    request_key: str = Field(min_length=8, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    user_message: Optional[str] = Field(default="", max_length=500)


class MemberOrderDetail(CheckoutSchema):
    id: int = Field(gt=0, strict=True)


class MemberOrderQuery(CheckoutSchema):
    """本人订单列表，tab 为页面分组而非后台状态编码。"""

    page: int = Field(default=1, ge=1, strict=True)
    pageSize: int = Field(default=20, ge=1, le=100, strict=True)
    tab: Literal["all", "pay", "send", "receive", "done"] = "all"


class MemberOrderSummary(CheckoutSchema):
    """仅允许读取当前会员汇总，不接收身份字段。"""
