from app.api.v1.system.goods.controller import GoodsRouter
from app.api.v1.system.goods_comment.controller import GoodsCommentRouter
# -*- coding: utf-8 -*-
"""系统核心路由聚合"""

from fastapi import APIRouter

from .address.controller import AddressRouter
from .ad.controller import AdRouter
from .after_sale.controller import AfterSaleRouter
from .ai_assistant.controller import AiAssistantRouter
from .auth.controller import AuthRouter
from .brand.controller import BrandRouter
from .category.controller import CategoryRouter
from .cart.controller import CartRouter
from .coupon.controller import CouponRouter
from .department.controller import DepartmentRouter
from .faq.controller import FaqRouter
from .favorite.controller import FavoriteRouter
from .feedback.controller import FeedbackRouter
from .footprint.controller import FootprintRouter
from .group_activity.controller import GroupActivityRouter
from .group_rule.controller import GroupRuleRouter
from .id_center.controller import IdCenterRouter
from .keyword.controller import KeywordRouter
from .login_record.controller import LoginRecordRouter
from .operation_log.controller import OperationLogRouter
from .order.controller import OrderRouter
from .lookup.controller import LookupRouter
from .member.controller import MemberRouter
from .menu.controller import MenuRouter
from .region.controller import RegionRouter
from .roles.controller import RolesRouter
from .search_history.controller import SearchHistoryRouter
from .statistic.controller import StatisticRouter
from .topic.controller import TopicRouter
from .user.controller import UserRouter

system_router = APIRouter()

system_router.include_router(AuthRouter)
system_router.include_router(AiAssistantRouter)
system_router.include_router(UserRouter)
system_router.include_router(MenuRouter)
system_router.include_router(RolesRouter)
system_router.include_router(LookupRouter)
system_router.include_router(MemberRouter)
system_router.include_router(AddressRouter)
system_router.include_router(AdRouter)
system_router.include_router(FavoriteRouter)
system_router.include_router(FootprintRouter)
system_router.include_router(SearchHistoryRouter)
system_router.include_router(StatisticRouter)
system_router.include_router(TopicRouter)
system_router.include_router(FeedbackRouter)
system_router.include_router(BrandRouter)
system_router.include_router(CategoryRouter)
system_router.include_router(CartRouter)
system_router.include_router(CouponRouter)
system_router.include_router(GroupRuleRouter)
system_router.include_router(GroupActivityRouter)
system_router.include_router(OrderRouter)
system_router.include_router(AfterSaleRouter)
system_router.include_router(RegionRouter)
system_router.include_router(FaqRouter)
system_router.include_router(KeywordRouter)
system_router.include_router(IdCenterRouter)
system_router.include_router(DepartmentRouter)
system_router.include_router(LoginRecordRouter)
system_router.include_router(OperationLogRouter)

system_router.include_router(GoodsRouter)
system_router.include_router(GoodsCommentRouter)
