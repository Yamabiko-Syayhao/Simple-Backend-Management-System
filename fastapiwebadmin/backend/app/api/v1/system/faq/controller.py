# -*- coding: utf-8 -*-
"""通用问题接口层

说明：`/list` 是公开接口（已加入 WHITE_ROUTER），客户端未登录也能读取 FAQ 展示；
      新增/编辑/删除仍然要后台权限。
"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.faq.schema import FaqDel, FaqIn, FaqQuery
from app.api.v1.system.faq.service import FaqService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

FaqRouter = APIRouter(prefix="/faq", tags=["通用问题"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@FaqRouter.post("/list", description="通用问题列表（客户端也可读）")
async def faq_list(params: FaqQuery):
    data = await FaqService.list(params)
    return await HttpResponse.success(data)


@FaqRouter.post("/detail", description="通用问题详情")
async def faq_detail(
    params: FaqDel,
    _auth=Depends(AuthPermission(["faq:query"], check_data_scope=False)),
):
    data = await FaqService.detail(params.id)
    return await HttpResponse.success(data)


@FaqRouter.post("/saveOrUpdate", description="新增或编辑通用问题")
async def faq_save_or_update(
    params: FaqIn,
    _auth=Depends(AuthPermission(["faq:add", "faq:edit"])),
):
    data = await FaqService.save_or_update(params)
    return await HttpResponse.success(data)


@FaqRouter.post("/deleted", description="删除通用问题")
async def faq_deleted(params: FaqDel, _auth=Depends(AuthPermission(["faq:delete"]))):
    await FaqService.deleted(params.id)
    return await HttpResponse.success()


@FaqRouter.post("/export", description="导出通用问题 xlsx")
async def faq_export(
    params: FaqQuery,
    _auth=Depends(AuthPermission(["faq:export"], check_data_scope=False)),
):
    content, filename = await FaqService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=faq.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)
