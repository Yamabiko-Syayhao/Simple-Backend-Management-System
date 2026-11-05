# -*- coding: utf-8 -*-
"""售后管理接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.after_sale.schema import AfterSaleAuditIn, AfterSaleDel, AfterSaleQuery
from app.api.v1.system.after_sale.service import AfterSaleService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

AfterSaleRouter = APIRouter(prefix="/afterSale", tags=["售后管理"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@AfterSaleRouter.post("/list", description="售后列表")
async def after_sale_list(
    params: AfterSaleQuery,
    _auth=Depends(AuthPermission(["afterSale:query"])),
):
    data = await AfterSaleService.list(params)
    return await HttpResponse.success(data)


@AfterSaleRouter.post("/detail", description="售后详情")
async def after_sale_detail(
    params: AfterSaleDel,
    _auth=Depends(AuthPermission(["afterSale:query"], check_data_scope=False)),
):
    data = await AfterSaleService.detail(params.id)
    return await HttpResponse.success(data)


@AfterSaleRouter.post("/audit", description="批量通过 / 批量拒绝")
async def after_sale_audit(
    params: AfterSaleAuditIn,
    _auth=Depends(AuthPermission(["afterSale:audit"])),
):
    count = await AfterSaleService.audit(params)
    return await HttpResponse.success({"count": count}, msg="操作成功")


@AfterSaleRouter.post("/export", description="导出售后 xlsx")
async def after_sale_export(
    params: AfterSaleQuery,
    _auth=Depends(AuthPermission(["afterSale:export"], check_data_scope=False)),
):
    content, filename = await AfterSaleService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=after_sale.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)
