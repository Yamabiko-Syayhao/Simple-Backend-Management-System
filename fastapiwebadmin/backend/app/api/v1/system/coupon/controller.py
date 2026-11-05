# -*- coding: utf-8 -*-
"""优惠券管理接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.coupon.schema import CouponClaimIn, CouponDel, CouponIn, CouponMineQuery, CouponQuery, CouponUserQuery
from app.api.v1.system.coupon.service import CouponService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

CouponRouter = APIRouter(prefix="/coupon", tags=["优惠券管理"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@CouponRouter.post("/list", description="优惠券列表")
async def coupon_list(params: CouponQuery, _auth=Depends(AuthPermission(["coupon:query"]))):
    data = await CouponService.list(params)
    return await HttpResponse.success(data)


@CouponRouter.post("/detail", description="优惠券详情")
async def coupon_detail(
    params: CouponDel,
    _auth=Depends(AuthPermission(["coupon:query"], check_data_scope=False)),
):
    data = await CouponService.detail(params.id)
    return await HttpResponse.success(data)


@CouponRouter.post("/userList", description="优惠券领取与使用记录")
async def coupon_user_list(
    params: CouponUserQuery,
    _auth=Depends(AuthPermission(["coupon:query"], check_data_scope=False)),
):
    data = await CouponService.user_list(params)
    return await HttpResponse.success(data)


@CouponRouter.post("/saveOrUpdate", description="新增或编辑优惠券")
async def coupon_save_or_update(
    params: CouponIn,
    _auth=Depends(AuthPermission(["coupon:add", "coupon:edit"])),
):
    data = await CouponService.save_or_update(params)
    return await HttpResponse.success(data)


@CouponRouter.post("/deleted", description="删除优惠券")
async def coupon_deleted(params: CouponDel, _auth=Depends(AuthPermission(["coupon:delete"]))):
    await CouponService.deleted(params.id)
    return await HttpResponse.success()


@CouponRouter.post("/export", description="导出优惠券 xlsx")
async def coupon_export(
    params: CouponQuery,
    _auth=Depends(AuthPermission(["coupon:export"], check_data_scope=False)),
):
    content, filename = await CouponService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=coupon.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)


# ---------------------------------------------------------------- 客户端（只读，无需后台权限）

@CouponRouter.post("/clientList", description="客户端可领取优惠券")
async def coupon_client_list():
    return await HttpResponse.success(await CouponService.client_list())


@CouponRouter.post("/claim", description="会员领取首页优惠券")
async def coupon_claim(params: CouponClaimIn):
    data = await CouponService.claim(params.id)
    return await HttpResponse.success(data)


@CouponRouter.post("/myList", description="会员本人的优惠券")
async def coupon_my_list(params: CouponMineQuery):
    data = await CouponService.my_list(params)
    return await HttpResponse.success(data)
