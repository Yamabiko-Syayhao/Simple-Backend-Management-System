"""商品管理接口层。"""
from urllib.parse import quote
from fastapi import Depends
from starlette.responses import StreamingResponse
from app.shared.router import APIRouter
from app.core.dependencies import AuthPermission
from app.utils.response import HttpResponse
from app.api.v1.system.goods.schema import GoodsQuery, GoodsIn, GoodsDel, GoodsBatchDel, GoodsChildIn, GoodsChildDel, GoodsClientQuery
from app.api.v1.system.goods.service import GoodsService

GoodsRouter = APIRouter(prefix="/goods", tags=["商品管理"])

@GoodsRouter.post("/list", description="商品列表")
async def goods_list(params: GoodsQuery, _auth=Depends(AuthPermission(["goods:query"], check_data_scope=False))):
    return await HttpResponse.success(await GoodsService.list(params))

@GoodsRouter.post("/detail", description="商品详情")
async def goods_detail(params: GoodsDel, _auth=Depends(AuthPermission(["goods:query"], check_data_scope=False))):
    return await HttpResponse.success(await GoodsService.detail(params.id))

async def require_goods_write(params: GoodsIn):
    return await AuthPermission(["goods:edit" if params.id else "goods:add"], check_data_scope=False)()


@GoodsRouter.post("/saveOrUpdate", description="商品新增或编辑")
async def goods_save_or_update(params: GoodsIn, _auth=Depends(require_goods_write)):
    return await HttpResponse.success(await GoodsService.save_or_update(params))

@GoodsRouter.post("/deleted", description="商品删除")
async def goods_deleted(params: GoodsDel, _auth=Depends(AuthPermission(["goods:delete"], check_data_scope=False))):
    return await HttpResponse.success(await GoodsService.deleted([params.id]))

@GoodsRouter.post("/batchDeleted", description="商品批量删除")
async def goods_batch_deleted(params: GoodsBatchDel, _auth=Depends(AuthPermission(["goods:delete"], check_data_scope=False))):
    return await HttpResponse.success(await GoodsService.deleted(params.ids))

@GoodsRouter.post("/specification/save", description="商品规格设置")
async def goods_specification_save(params: GoodsChildIn, _auth=Depends(AuthPermission(["goods:edit"], check_data_scope=False))):
    return await HttpResponse.success(await GoodsService.save_child("specification", params))

@GoodsRouter.post("/product/save", description="商品库存设置")
async def goods_product_save(params: GoodsChildIn, _auth=Depends(AuthPermission(["goods:edit"], check_data_scope=False))):
    return await HttpResponse.success(await GoodsService.save_child("product", params))

@GoodsRouter.post("/attribute/save", description="商品参数保存")
async def goods_attribute_save(params: GoodsChildIn, _auth=Depends(AuthPermission(["goods:edit"], check_data_scope=False))):
    return await HttpResponse.success(await GoodsService.save_child("attribute", params))

@GoodsRouter.post("/attribute/deleted", description="商品参数删除")
async def goods_attribute_deleted(params: GoodsChildDel, _auth=Depends(AuthPermission(["goods:edit"], check_data_scope=False))):
    return await HttpResponse.success(await GoodsService.delete_attribute(params))

@GoodsRouter.post("/export", description="导出商品")
async def goods_export(params: GoodsQuery, _auth=Depends(AuthPermission(["goods:export"], check_data_scope=False))):
    content, filename = await GoodsService.export(params)
    return StreamingResponse(iter([content]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=goods.xlsx; filename*=UTF-8''" + quote(filename)})


# ---------------------------------------------------------------- 客户端（只读，无需后台权限）

@GoodsRouter.post("/clientList", description="客户端商品列表/搜索")
async def goods_client_list(params: GoodsClientQuery):
    return await HttpResponse.success(await GoodsService.client_list(params))


@GoodsRouter.post("/clientDetail", description="客户端商品详情")
async def goods_client_detail(params: GoodsDel):
    return await HttpResponse.success(await GoodsService.client_detail(params.id))
