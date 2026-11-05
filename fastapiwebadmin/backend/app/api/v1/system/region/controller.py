# -*- coding: utf-8 -*-
"""行政区域接口层

注意：这是基础字典数据，**不加 AuthPermission**，客户端（会员）也能直接查询。
为了让游客在注册/选地址时也能用，这两个接口已加入 WHITE_ROUTER 白名单。
"""

from app.api.v1.system.region.schema import RegionChildrenIn
from app.api.v1.system.region.service import RegionService
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

RegionRouter = APIRouter(prefix="/region", tags=["行政区域"])


@RegionRouter.post("/tree", description="行政区域三级树（省/市/区）")
async def region_tree():
    data = await RegionService.tree()
    return await HttpResponse.success(data)


@RegionRouter.post("/children", description="查询某个区域的直接下级")
async def region_children(params: RegionChildrenIn):
    data = await RegionService.children(params.parent_id or 0)
    return await HttpResponse.success(data)
