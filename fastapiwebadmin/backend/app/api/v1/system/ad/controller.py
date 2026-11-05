# -*- coding: utf-8 -*-
"""广告管理接口层"""

from urllib.parse import quote

from fastapi import Depends, File, UploadFile
from starlette.responses import StreamingResponse

from app.api.v1.system.ad.schema import AdBannerQuery, AdDel, AdIn, AdQuery
from app.api.v1.system.ad.service import AdService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

AdRouter = APIRouter(prefix="/ad", tags=["广告管理"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@AdRouter.post("/list", description="广告列表")
async def ad_list(params: AdQuery, _auth=Depends(AuthPermission(["ad:query"]))):
    data = await AdService.list(params)
    return await HttpResponse.success(data)


@AdRouter.post("/detail", description="广告详情")
async def ad_detail(
    params: AdDel,
    _auth=Depends(AuthPermission(["ad:query"], check_data_scope=False)),
):
    data = await AdService.detail(params.id)
    return await HttpResponse.success(data)


@AdRouter.post("/saveOrUpdate", description="新增或编辑广告")
async def ad_save_or_update(
    params: AdIn,
    _auth=Depends(AuthPermission(["ad:add", "ad:edit"])),
):
    data = await AdService.save_or_update(params)
    return await HttpResponse.success(data)


@AdRouter.post("/deleted", description="删除广告")
async def ad_deleted(params: AdDel, _auth=Depends(AuthPermission(["ad:delete"]))):
    await AdService.deleted(params.id)
    return await HttpResponse.success()


@AdRouter.post("/export", description="导出广告 xlsx")
async def ad_export(
    params: AdQuery,
    _auth=Depends(AuthPermission(["ad:export"], check_data_scope=False)),
):
    content, filename = await AdService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=ad.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)


@AdRouter.post("/upload", description="上传广告图片（不超过3MB）")
async def ad_upload(
    file: UploadFile = File(...),
    _auth=Depends(AuthPermission(["ad:add", "ad:edit"], check_data_scope=False)),
):
    data = await AdService.upload(file)
    return await HttpResponse.success(data)


@AdRouter.post("/banners", description="客户端首页已启用轮播广告")
async def ad_banners(params: AdBannerQuery):
    data = await AdService.banners(params.position)
    return await HttpResponse.success(data)
