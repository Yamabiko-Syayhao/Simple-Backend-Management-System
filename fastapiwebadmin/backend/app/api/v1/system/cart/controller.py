# -*- coding: utf-8 -*-
"""客户端购物车接口；需会员 token，不开放白名单或后台权限。"""

from app.api.v1.system.cart.schema import CartChecked, CartDel, CartIn, CartQuery, CartUpdate
from app.api.v1.system.cart.service import CartService
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

CartRouter = APIRouter(prefix="/cart", tags=["会员购物车"])


@CartRouter.post("/list", description="当前会员购物车")
async def cart_list(params: CartQuery):
    data = await CartService.list()
    return await HttpResponse.success(data)


@CartRouter.post("/add", description="加入购物车，同规格合并数量")
async def cart_add(params: CartIn):
    data = await CartService.add(params)
    return await HttpResponse.success(data)


@CartRouter.post("/update", description="修改购物车商品数量")
async def cart_update(params: CartUpdate):
    data = await CartService.update(params)
    return await HttpResponse.success(data)


@CartRouter.post("/checked", description="单选或批量勾选购物车条目")
async def cart_checked(params: CartChecked):
    data = await CartService.checked(params)
    return await HttpResponse.success(data)


@CartRouter.post("/deleted", description="物理删除当前会员购物车条目")
async def cart_deleted(params: CartDel):
    data = await CartService.deleted(params)
    return await HttpResponse.success(data)


@CartRouter.post("/count", description="当前会员购物车商品总件数")
async def cart_count(params: CartQuery):
    data = await CartService.count()
    return await HttpResponse.success(data)
