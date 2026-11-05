# -*- coding: utf-8 -*-
"""统计报表接口：首页总量 + 用户 / 订单 / 商品趋势。"""

from fastapi import Depends

from app.api.v1.system.statistic.schema import StatisticChartQuery, StatisticQuery
from app.api.v1.system.statistic.service import StatisticService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

StatisticRouter = APIRouter(prefix="/statistic", tags=["统计报表"])


@StatisticRouter.post("/countStatistic", description="商城会员、商品、货品与订单总量")
async def statistic_count(
    params: StatisticQuery,
    _auth=Depends(AuthPermission(check_data_scope=False)),
):
    data = await StatisticService.count_statistic()
    return await HttpResponse.success(data)


@StatisticRouter.post("/userChart", description="用户统计：每日新增会员数")
async def statistic_user_chart(
    params: StatisticChartQuery,
    _auth=Depends(AuthPermission(check_data_scope=False)),
):
    return await HttpResponse.success(await StatisticService.user_chart(params.days or 0))


@StatisticRouter.post("/orderChart", description="订单统计：每日订单量/下单用户/订单总额/客单价")
async def statistic_order_chart(
    params: StatisticChartQuery,
    _auth=Depends(AuthPermission(check_data_scope=False)),
):
    return await HttpResponse.success(await StatisticService.order_chart(params.days or 0))


@StatisticRouter.post("/goodsChart", description="商品统计：每日订单量/下单货品数量/下单货品总额")
async def statistic_goods_chart(
    params: StatisticChartQuery,
    _auth=Depends(AuthPermission(check_data_scope=False)),
):
    return await HttpResponse.success(await StatisticService.goods_chart(params.days or 0))
