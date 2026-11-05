# -*- coding: utf-8 -*-
"""品牌制造商接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.brand.schema import BrandDel, BrandIn, BrandQuery
from app.api.v1.system.brand.service import BrandService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

BrandRouter = APIRouter(prefix="/brand", tags=["品牌制造商"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@BrandRouter.post("/list", description="品牌商列表")
async def brand_list(params: BrandQuery, _auth=Depends(AuthPermission(["brand:query"]))):
    data = await BrandService.list(params)
    return await HttpResponse.success(data)


@BrandRouter.post("/detail", description="品牌商详情")
async def brand_detail(
    params: BrandDel,
    _auth=Depends(AuthPermission(["brand:query"], check_data_scope=False)),
):
    data = await BrandService.detail(params.id)
    return await HttpResponse.success(data)


@BrandRouter.post("/saveOrUpdate", description="新增或编辑品牌商")
async def brand_save_or_update(
    params: BrandIn,
    _auth=Depends(AuthPermission(["brand:add", "brand:edit"])),
):
    data = await BrandService.save_or_update(params)
    return await HttpResponse.success(data)


@BrandRouter.post("/deleted", description="删除品牌商")
async def brand_deleted(params: BrandDel, _auth=Depends(AuthPermission(["brand:delete"]))):
    await BrandService.deleted(params.id)
    return await HttpResponse.success()


@BrandRouter.post("/export", description="导出品牌商 xlsx")
async def brand_export(
    params: BrandQuery,
    _auth=Depends(AuthPermission(["brand:export"], check_data_scope=False)),
):
    content, filename = await BrandService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=brand.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)


# ---------------------------------------------------------------- 客户端（只读，无需后台权限）

@BrandRouter.post("/clientList", description="客户端品牌商列表")
async def brand_client_list(params: BrandQuery):
    return await HttpResponse.success(await BrandService.client_list(params))


@BrandRouter.post("/clientDetail", description="客户端品牌商详情")
async def brand_client_detail(params: BrandDel):
    return await HttpResponse.success(await BrandService.client_detail(params.id))
