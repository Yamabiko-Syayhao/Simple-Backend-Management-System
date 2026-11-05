# -*- coding: utf-8 -*-
"""团购活动接口层

后台只读：列表（展开查看参与成员）+ 导出。数据由客户端开团/参团时写入。
"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.group_activity.schema import GroupActivityQuery
from app.api.v1.system.group_activity.service import GroupActivityService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

GroupActivityRouter = APIRouter(prefix="/groupActivity", tags=["团购活动"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@GroupActivityRouter.post("/list", description="团购活动列表")
async def group_activity_list(
    params: GroupActivityQuery,
    _auth=Depends(AuthPermission(["groupActivity:query"], check_data_scope=False)),
):
    return await HttpResponse.success(await GroupActivityService.list(params))


@GroupActivityRouter.post("/export", description="导出团购活动")
async def group_activity_export(
    params: GroupActivityQuery,
    _auth=Depends(AuthPermission(["groupActivity:export"], check_data_scope=False)),
):
    content, filename = await GroupActivityService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=group_activity.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)
