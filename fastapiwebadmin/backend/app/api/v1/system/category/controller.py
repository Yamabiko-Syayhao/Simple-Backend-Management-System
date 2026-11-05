# -*- coding: utf-8 -*-
"""商品类目接口层"""

from fastapi import Depends

from app.api.v1.system.category.schema import CategoryDel, CategoryIn
from app.api.v1.system.category.service import CategoryService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

CategoryRouter = APIRouter(prefix="/category", tags=["商品类目"])


@CategoryRouter.post("/list", description="商品类目列表（全量，前端组装成树）")
async def category_list(_auth=Depends(AuthPermission(["category:query"]))):
    data = await CategoryService.list()
    return await HttpResponse.success(data)


@CategoryRouter.post("/detail", description="商品类目详情")
async def category_detail(
    params: CategoryDel,
    _auth=Depends(AuthPermission(["category:query"], check_data_scope=False)),
):
    data = await CategoryService.detail(params.id)
    return await HttpResponse.success(data)


@CategoryRouter.post("/saveOrUpdate", description="新增或编辑类目")
async def category_save_or_update(
    params: CategoryIn,
    _auth=Depends(AuthPermission(["category:add", "category:edit"])),
):
    data = await CategoryService.save_or_update(params)
    return await HttpResponse.success(data)


@CategoryRouter.post("/deleted", description="删除类目")
async def category_deleted(params: CategoryDel, _auth=Depends(AuthPermission(["category:delete"]))):
    await CategoryService.deleted(params.id)
    return await HttpResponse.success()


# ---------------------------------------------------------------- 客户端（只读，无需后台权限）

@CategoryRouter.post("/clientList", description="客户端一级类目（首页快捷入口）")
async def category_client_list():
    return await HttpResponse.success(await CategoryService.client_list())


@CategoryRouter.post("/clientTree", description="客户端完整两级商品类目树")
async def category_client_tree():
    data = await CategoryService.client_tree()
    return await HttpResponse.success(data)
