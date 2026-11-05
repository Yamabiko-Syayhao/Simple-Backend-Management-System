# -*- coding: utf-8 -*-
"""专题管理接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.topic.schema import TopicBatchDel, TopicDel, TopicIn, TopicQuery
from app.api.v1.system.topic.service import TopicService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

TopicRouter = APIRouter(prefix="/topic", tags=["专题管理"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@TopicRouter.post("/list", description="专题列表")
async def topic_list(params: TopicQuery, _auth=Depends(AuthPermission(["topic:query"]))):
    data = await TopicService.list(params)
    return await HttpResponse.success(data)


@TopicRouter.post("/detail", description="专题详情")
async def topic_detail(
    params: TopicDel,
    _auth=Depends(AuthPermission(["topic:query"], check_data_scope=False)),
):
    data = await TopicService.detail(params.id)
    return await HttpResponse.success(data)


@TopicRouter.post("/saveOrUpdate", description="创建或编辑专题")
async def topic_save_or_update(
    params: TopicIn,
    _auth=Depends(AuthPermission(["topic:add", "topic:edit"])),
):
    data = await TopicService.save_or_update(params)
    return await HttpResponse.success(data)


@TopicRouter.post("/deleted", description="删除专题")
async def topic_deleted(params: TopicDel, _auth=Depends(AuthPermission(["topic:delete"]))):
    await TopicService.deleted(params.id)
    return await HttpResponse.success()


@TopicRouter.post("/batchDeleted", description="批量删除专题")
async def topic_batch_deleted(params: TopicBatchDel, _auth=Depends(AuthPermission(["topic:delete"]))):
    data = await TopicService.batch_deleted(params.ids)
    return await HttpResponse.success(data)


@TopicRouter.post("/export", description="导出专题 xlsx")
async def topic_export(
    params: TopicQuery,
    _auth=Depends(AuthPermission(["topic:export"], check_data_scope=False)),
):
    content, filename = await TopicService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=topic.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)


@TopicRouter.post("/clientList", description="客户端专题列表")
async def topic_client_list(params: TopicQuery):
    data = await TopicService.client_list(params)
    return await HttpResponse.success(data)


@TopicRouter.post("/clientDetail", description="客户端专题详情及在售商品")
async def topic_client_detail(params: TopicDel):
    data = await TopicService.client_detail(params.id)
    return await HttpResponse.success(data)
