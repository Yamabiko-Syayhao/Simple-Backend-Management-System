# -*- coding: utf-8 -*-
"""搜索关键词接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.keyword.schema import KeywordDel, KeywordIn, KeywordQuery
from app.api.v1.system.keyword.service import KeywordService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

KeywordRouter = APIRouter(prefix="/keyword", tags=["关键词"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@KeywordRouter.post("/list", description="关键词列表")
async def keyword_list(params: KeywordQuery, _auth=Depends(AuthPermission(["keyword:query"]))):
    data = await KeywordService.list(params)
    return await HttpResponse.success(data)


@KeywordRouter.post("/detail", description="关键词详情")
async def keyword_detail(
    params: KeywordDel,
    _auth=Depends(AuthPermission(["keyword:query"], check_data_scope=False)),
):
    data = await KeywordService.detail(params.id)
    return await HttpResponse.success(data)


@KeywordRouter.post("/saveOrUpdate", description="新增或编辑关键词")
async def keyword_save_or_update(
    params: KeywordIn,
    _auth=Depends(AuthPermission(["keyword:add", "keyword:edit"])),
):
    data = await KeywordService.save_or_update(params)
    return await HttpResponse.success(data)


@KeywordRouter.post("/deleted", description="删除关键词")
async def keyword_deleted(params: KeywordDel, _auth=Depends(AuthPermission(["keyword:delete"]))):
    await KeywordService.deleted(params.id)
    return await HttpResponse.success()


@KeywordRouter.post("/export", description="导出关键词 xlsx")
async def keyword_export(
    params: KeywordQuery,
    _auth=Depends(AuthPermission(["keyword:export"], check_data_scope=False)),
):
    content, filename = await KeywordService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=keyword.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)
