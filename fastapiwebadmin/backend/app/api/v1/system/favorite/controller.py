# -*- coding: utf-8 -*-
"""会员收藏接口层"""

from urllib.parse import quote

from fastapi import Depends
from starlette.responses import StreamingResponse

from app.api.v1.system.favorite.schema import FavoriteDel, FavoriteIn, FavoriteQuery, FavoriteMineQuery, FavoriteMineDel, FavoriteMineSet
from app.api.v1.system.favorite.service import FavoriteService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

FavoriteRouter = APIRouter(prefix="/favorite", tags=["会员收藏"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@FavoriteRouter.post("/myList", description="当前会员收藏商品分页列表")
async def favorite_my_list(params: FavoriteMineQuery):
    data = await FavoriteService.my_list(params)
    return await HttpResponse.success(data)


@FavoriteRouter.post("/myDeleted", description="会员取消本人的一条收藏")
async def favorite_my_deleted(params: FavoriteMineDel):
    data = await FavoriteService.my_deleted(params.id)
    return await HttpResponse.success(data)


@FavoriteRouter.post("/mySet", description="会员设置商品收藏状态")
async def favorite_my_set(params: FavoriteMineSet):
    data = await FavoriteService.my_set(params)
    return await HttpResponse.success(data)


@FavoriteRouter.post("/list", description="会员收藏列表")
async def favorite_list(params: FavoriteQuery, _auth=Depends(AuthPermission(["favorite:query"]))):
    data = await FavoriteService.list(params)
    return await HttpResponse.success(data)


@FavoriteRouter.post("/detail", description="会员收藏详情")
async def favorite_detail(
    params: FavoriteDel,
    _auth=Depends(AuthPermission(["favorite:query"], check_data_scope=False)),
):
    data = await FavoriteService.detail(params.id)
    return await HttpResponse.success(data)


@FavoriteRouter.post("/saveOrUpdate", description="新增或编辑收藏")
async def favorite_save_or_update(
    params: FavoriteIn,
    _auth=Depends(AuthPermission(["favorite:add", "favorite:edit"])),
):
    await FavoriteService.save_or_update(params)
    return await HttpResponse.success()


@FavoriteRouter.post("/deleted", description="删除收藏")
async def favorite_deleted(params: FavoriteDel, _auth=Depends(AuthPermission(["favorite:delete"]))):
    await FavoriteService.deleted(params.id)
    return await HttpResponse.success()


@FavoriteRouter.post("/export", description="导出会员收藏 xlsx")
async def favorite_export(
    params: FavoriteQuery,
    _auth=Depends(AuthPermission(["favorite:export"], check_data_scope=False)),
):
    content, filename = await FavoriteService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=favorite.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)
