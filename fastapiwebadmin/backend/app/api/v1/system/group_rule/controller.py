# -*- coding: utf-8 -*-
"""团购规则接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.group_rule.schema import GroupRuleDel, GroupRuleIn, GroupRuleQuery
from app.api.v1.system.group_rule.service import GroupRuleService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

GroupRuleRouter = APIRouter(prefix="/groupRule", tags=["团购规则"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@GroupRuleRouter.post("/list", description="团购规则列表")
async def group_rule_list(
    params: GroupRuleQuery,
    _auth=Depends(AuthPermission(["groupRule:query"], check_data_scope=False)),
):
    return await HttpResponse.success(await GroupRuleService.list(params))


@GroupRuleRouter.post("/detail", description="团购规则详情")
async def group_rule_detail(
    params: GroupRuleDel,
    _auth=Depends(AuthPermission(["groupRule:query"], check_data_scope=False)),
):
    return await HttpResponse.success(await GroupRuleService.detail(params.id))


@GroupRuleRouter.post("/saveOrUpdate", description="新增或编辑团购规则")
async def group_rule_save_or_update(
    params: GroupRuleIn,
    _auth=Depends(AuthPermission(["groupRule:add", "groupRule:edit"], check_data_scope=False)),
):
    return await HttpResponse.success(await GroupRuleService.save_or_update(params))


@GroupRuleRouter.post("/deleted", description="删除团购规则")
async def group_rule_deleted(
    params: GroupRuleDel,
    _auth=Depends(AuthPermission(["groupRule:delete"], check_data_scope=False)),
):
    await GroupRuleService.deleted(params.id)
    return await HttpResponse.success()


@GroupRuleRouter.post("/export", description="导出团购规则")
async def group_rule_export(
    params: GroupRuleQuery,
    _auth=Depends(AuthPermission(["groupRule:export"], check_data_scope=False)),
):
    content, filename = await GroupRuleService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=group_rule.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)


# ---------------------------------------------------------------- 客户端（只读，无需后台权限）

@GroupRuleRouter.post("/clientList", description="客户端进行中的团购规则")
async def group_rule_client_list():
    return await HttpResponse.success(await GroupRuleService.client_list())
