# -*- coding: utf-8 -*-
"""会员意见反馈接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.feedback.schema import FeedbackDel, FeedbackIn, FeedbackQuery, FeedbackMineIn, FeedbackContactQuery
from app.api.v1.system.feedback.service import FeedbackService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

FeedbackRouter = APIRouter(prefix="/feedback", tags=["意见反馈"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@FeedbackRouter.post("/mySubmit", description="当前会员提交意见反馈")
async def feedback_my_submit(params: FeedbackMineIn):
    data = await FeedbackService.my_submit(params)
    return await HttpResponse.success(data)


@FeedbackRouter.post("/contact", description="服务中心公开联系方式白名单")
async def feedback_contact(params: FeedbackContactQuery):
    data = await FeedbackService.contact()
    return await HttpResponse.success(data)


@FeedbackRouter.post("/list", description="意见反馈列表")
async def feedback_list(params: FeedbackQuery, _auth=Depends(AuthPermission(["feedback:query"]))):
    data = await FeedbackService.list(params)
    return await HttpResponse.success(data)


@FeedbackRouter.post("/detail", description="意见反馈详情")
async def feedback_detail(
    params: FeedbackDel,
    _auth=Depends(AuthPermission(["feedback:query"], check_data_scope=False)),
):
    data = await FeedbackService.detail(params.id)
    return await HttpResponse.success(data)


@FeedbackRouter.post("/saveOrUpdate", description="新增或编辑意见反馈")
async def feedback_save_or_update(
    params: FeedbackIn,
    _auth=Depends(AuthPermission(["feedback:add", "feedback:edit"])),
):
    await FeedbackService.save_or_update(params)
    return await HttpResponse.success()


@FeedbackRouter.post("/deleted", description="删除意见反馈")
async def feedback_deleted(params: FeedbackDel, _auth=Depends(AuthPermission(["feedback:delete"]))):
    await FeedbackService.deleted(params.id)
    return await HttpResponse.success()


@FeedbackRouter.post("/export", description="导出意见反馈 xlsx")
async def feedback_export(
    params: FeedbackQuery,
    _auth=Depends(AuthPermission(["feedback:export"], check_data_scope=False)),
):
    content, filename = await FeedbackService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=feedback.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)
