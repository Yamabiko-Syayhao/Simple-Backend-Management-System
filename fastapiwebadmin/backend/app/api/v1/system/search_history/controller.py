# -*- coding: utf-8 -*-
"""会员搜索历史接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.search_history.schema import (
    SearchHistoryDel,
    SearchHistoryIn,
    SearchHistoryKeywordIn,
    SearchHistoryQuery,
)
from app.api.v1.system.search_history.service import SearchHistoryService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

SearchHistoryRouter = APIRouter(prefix="/searchHistory", tags=["搜索历史"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@SearchHistoryRouter.post("/list", description="搜索历史列表")
async def search_history_list(
    params: SearchHistoryQuery,
    _auth=Depends(AuthPermission(["searchHistory:query"])),
):
    data = await SearchHistoryService.list(params)
    return await HttpResponse.success(data)


@SearchHistoryRouter.post("/detail", description="搜索历史详情")
async def search_history_detail(
    params: SearchHistoryDel,
    _auth=Depends(AuthPermission(["searchHistory:query"], check_data_scope=False)),
):
    data = await SearchHistoryService.detail(params.id)
    return await HttpResponse.success(data)


@SearchHistoryRouter.post("/saveOrUpdate", description="新增或编辑搜索历史")
async def search_history_save_or_update(
    params: SearchHistoryIn,
    _auth=Depends(AuthPermission(["searchHistory:add", "searchHistory:edit"])),
):
    await SearchHistoryService.save_or_update(params)
    return await HttpResponse.success()


@SearchHistoryRouter.post("/deleted", description="删除搜索历史")
async def search_history_deleted(
    params: SearchHistoryDel,
    _auth=Depends(AuthPermission(["searchHistory:delete"])),
):
    await SearchHistoryService.deleted(params.id)
    return await HttpResponse.success()


@SearchHistoryRouter.post("/export", description="导出搜索历史 xlsx")
async def search_history_export(
    params: SearchHistoryQuery,
    _auth=Depends(AuthPermission(["searchHistory:export"], check_data_scope=False)),
):
    content, filename = await SearchHistoryService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=search_history.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)


# ---------------------------------------------------------------- 客户端（会员本人，无需后台权限）

@SearchHistoryRouter.post("/myList", description="客户端：我的搜索历史")
async def search_history_my_list():
    return await HttpResponse.success(await SearchHistoryService.my_list())


@SearchHistoryRouter.post("/add", description="客户端：记录一次搜索")
async def search_history_add(params: SearchHistoryKeywordIn):
    await SearchHistoryService.add(params.keyword)
    return await HttpResponse.success()


@SearchHistoryRouter.post("/clear", description="客户端：清空我的搜索历史")
async def search_history_clear():
    await SearchHistoryService.clear()
    return await HttpResponse.success()
