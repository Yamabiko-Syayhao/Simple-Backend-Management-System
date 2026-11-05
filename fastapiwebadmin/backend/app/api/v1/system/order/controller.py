# -*- coding: utf-8 -*-
"""商城订单接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.order.schema import (
    OrderCollectIn,
    OrderDel,
    OrderDeliverIn,
    OrderQuery,
    OrderRefundIn,
)
from app.api.v1.system.order.service import OrderService
from app.api.v1.system.order.client_service import CheckoutService
from app.api.v1.system.order.schema import CheckoutPreview, CheckoutQuote, CheckoutSubmit, MemberOrderDetail, MemberOrderQuery, MemberOrderSummary
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

OrderRouter = APIRouter(prefix="/order", tags=["订单管理"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@OrderRouter.post("/myList", description="当前会员订单分页列表")
async def order_my_list(params: MemberOrderQuery):
    data = await OrderService.my_list(params)
    return await HttpResponse.success(data)


@OrderRouter.post("/mySummary", description="当前会员订单与优惠券数量")
async def order_my_summary(params: MemberOrderSummary):
    data = await OrderService.my_summary()
    return await HttpResponse.success(data)


@OrderRouter.post("/myDeleted", description="会员删除本人的已取消订单")
async def order_my_deleted(params: MemberOrderDetail):
    data = await OrderService.my_deleted(params.id)
    return await HttpResponse.success(data)

@OrderRouter.post("/preview", description="会员确认订单与实时优惠报价")
async def order_preview(params: CheckoutPreview):
    data = await CheckoutService.preview(params)
    return await HttpResponse.success(data)


@OrderRouter.post("/coupons", description="当前结算可用与不可用的本人优惠券")
async def order_coupons(params: CheckoutQuote):
    data = await CheckoutService.coupons(params)
    return await HttpResponse.success(data)


@OrderRouter.post("/submit", description="会员提交未付款订单")
async def order_submit(params: CheckoutSubmit):
    data = await CheckoutService.submit(params)
    return await HttpResponse.success(data)


@OrderRouter.post("/myDetail", description="会员本人订单与支付方式占位信息")
async def order_my_detail(params: MemberOrderDetail):
    data = await CheckoutService.my_detail(params.id)
    return await HttpResponse.success(data)


@OrderRouter.post("/list", description="订单列表")
async def order_list(params: OrderQuery, _auth=Depends(AuthPermission(["order:query"]))):
    data = await OrderService.list(params)
    return await HttpResponse.success(data)


@OrderRouter.post("/detail", description="订单详情")
async def order_detail(
    params: OrderDel,
    _auth=Depends(AuthPermission(["order:query"], check_data_scope=False)),
):
    data = await OrderService.detail(params.id)
    return await HttpResponse.success(data)


@OrderRouter.post("/deleted", description="删除订单")
async def order_deleted(params: OrderDel, _auth=Depends(AuthPermission(["order:delete"]))):
    await OrderService.deleted(params.id)
    return await HttpResponse.success()


@OrderRouter.post("/collect", description="订单收款（线下收款）")
async def order_collect(params: OrderCollectIn, _auth=Depends(AuthPermission(["order:collect"]))):
    await OrderService.collect(params)
    return await HttpResponse.success()


@OrderRouter.post("/deliver", description="订单发货")
async def order_deliver(params: OrderDeliverIn, _auth=Depends(AuthPermission(["order:deliver"]))):
    await OrderService.deliver(params)
    return await HttpResponse.success()


@OrderRouter.post("/refund", description="订单退款")
async def order_refund(params: OrderRefundIn, _auth=Depends(AuthPermission(["order:refund"]))):
    await OrderService.refund(params)
    return await HttpResponse.success()


@OrderRouter.post("/export", description="导出订单 xlsx")
async def order_export(
    params: OrderQuery,
    _auth=Depends(AuthPermission(["order:export"], check_data_scope=False)),
):
    content, filename = await OrderService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=order.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)
