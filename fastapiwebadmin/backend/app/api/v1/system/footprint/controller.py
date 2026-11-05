# -*- coding: utf-8 -*-
"""会员足迹接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.footprint.schema import FootprintDel, FootprintIn, FootprintQuery
from app.api.v1.system.footprint.service import FootprintService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

FootprintRouter = APIRouter(prefix="/footprint", tags=["会员足迹"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@FootprintRouter.post("/list", description="会员足迹列表")
async def footprint_list(params: FootprintQuery, _auth=Depends(AuthPermission(["footprint:query"]))):
    data = await FootprintService.list(params)
    return await HttpResponse.success(data)


@FootprintRouter.post("/detail", description="会员足迹详情")
async def footprint_detail(
    params: FootprintDel,
    _auth=Depends(AuthPermission(["footprint:query"], check_data_scope=False)),
):
    data = await FootprintService.detail(params.id)
    return await HttpResponse.success(data)


@FootprintRouter.post("/saveOrUpdate", description="新增或编辑足迹")
async def footprint_save_or_update(
    params: FootprintIn,
    _auth=Depends(AuthPermission(["footprint:add", "footprint:edit"])),
):
    await FootprintService.save_or_update(params)
    return await HttpResponse.success()


@FootprintRouter.post("/deleted", description="删除足迹")
async def footprint_deleted(params: FootprintDel, _auth=Depends(AuthPermission(["footprint:delete"]))):
    await FootprintService.deleted(params.id)
    return await HttpResponse.success()


@FootprintRouter.post("/export", description="导出会员足迹 xlsx")
async def footprint_export(
    params: FootprintQuery,
    _auth=Depends(AuthPermission(["footprint:export"], check_data_scope=False)),
):
    content, filename = await FootprintService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=footprint.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)
