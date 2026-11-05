# -*- coding: utf-8 -*-
"""收货地址接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.address.schema import (
    AddressClientId, AddressClientIn, AddressClientQuery,
    AddressDel, AddressIn, AddressQuery,
)
from app.api.v1.system.address.service import AddressService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

AddressRouter = APIRouter(prefix="/address", tags=["收货地址"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@AddressRouter.post("/list", description="收货地址列表")
async def address_list(params: AddressQuery, _auth=Depends(AuthPermission(["address:query"]))):
    data = await AddressService.list(params)
    return await HttpResponse.success(data)


@AddressRouter.post("/detail", description="收货地址详情")
async def address_detail(
    params: AddressDel,
    _auth=Depends(AuthPermission(["address:query"], check_data_scope=False)),
):
    data = await AddressService.detail(params.id)
    return await HttpResponse.success(data)


@AddressRouter.post("/saveOrUpdate", description="新增或编辑收货地址")
async def address_save_or_update(
    params: AddressIn,
    _auth=Depends(AuthPermission(["address:add", "address:edit"])),
):
    await AddressService.save_or_update(params)
    return await HttpResponse.success()


@AddressRouter.post("/deleted", description="删除收货地址")
async def address_deleted(params: AddressDel, _auth=Depends(AuthPermission(["address:delete"]))):
    await AddressService.deleted(params.id)
    return await HttpResponse.success()


@AddressRouter.post("/export", description="导出收货地址 xlsx")
async def address_export(
    params: AddressQuery,
    _auth=Depends(AuthPermission(["address:export"], check_data_scope=False)),
):
    content, filename = await AddressService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=address.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)


# ------------------------------------------------------------------ 会员本人（不加入公开白名单）
@AddressRouter.post("/myList", description="当前会员收货地址")
async def address_my_list(params: AddressClientQuery):
    data = await AddressService.my_list()
    return await HttpResponse.success(data)


@AddressRouter.post("/myDetail", description="当前会员收货地址详情")
async def address_my_detail(params: AddressClientId):
    data = await AddressService.my_detail(params.id)
    return await HttpResponse.success(data)


@AddressRouter.post("/mySave", description="会员新增或编辑本人收货地址")
async def address_my_save(params: AddressClientIn):
    data = await AddressService.my_save(params)
    return await HttpResponse.success(data)


@AddressRouter.post("/myDeleted", description="会员物理删除本人收货地址")
async def address_my_deleted(params: AddressClientId):
    await AddressService.my_deleted(params.id)
    return await HttpResponse.success({})


@AddressRouter.post("/myDefault", description="会员设置默认收货地址")
async def address_my_default(params: AddressClientId):
    data = await AddressService.my_default(params.id)
    return await HttpResponse.success(data)
