# -*- coding: utf-8 -*-
"""商品评论接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.goods_comment.schema import (
    GoodsCommentDel,
    GoodsCommentQuery,
    GoodsCommentReplyIn,
)
from app.api.v1.system.goods_comment.service import GoodsCommentService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

GoodsCommentRouter = APIRouter(prefix="/goodsComment", tags=["商品评论"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@GoodsCommentRouter.post("/list", description="商品评论列表")
async def goods_comment_list(
    params: GoodsCommentQuery,
    _auth=Depends(AuthPermission(["goodsComment:query"], check_data_scope=False)),
):
    return await HttpResponse.success(await GoodsCommentService.list(params))


@GoodsCommentRouter.post("/reply", description="回复评论")
async def goods_comment_reply(
    params: GoodsCommentReplyIn,
    _auth=Depends(AuthPermission(["goodsComment:reply"], check_data_scope=False)),
):
    return await HttpResponse.success(await GoodsCommentService.reply(params), msg="回复成功")


@GoodsCommentRouter.post("/deleted", description="删除评论")
async def goods_comment_deleted(
    params: GoodsCommentDel,
    _auth=Depends(AuthPermission(["goodsComment:delete"], check_data_scope=False)),
):
    await GoodsCommentService.deleted(params.id)
    return await HttpResponse.success()


@GoodsCommentRouter.post("/export", description="导出商品评论")
async def goods_comment_export(
    params: GoodsCommentQuery,
    _auth=Depends(AuthPermission(["goodsComment:export"], check_data_scope=False)),
):
    content, filename = await GoodsCommentService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=goods_comment.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)
