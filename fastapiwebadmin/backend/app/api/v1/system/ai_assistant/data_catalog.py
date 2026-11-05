"""助手可读取的数据表和字段。新增字段必须显式加入清单。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TableAccess:
    title: str
    permission: str
    fields: str
    relations: str = ""


# 普通管理员使用后台现有查询权限。只有超管可读取无对应后台列表的内部表。
SUPER_ADMIN_ONLY = "@super_admin"
SOLAR_SCHEDULE = "celery_solar_schedule"
TABLES = {
    "mal_goods": TableAccess("商品", "goods:query",
        "name goods_sn retail_price market_price is_on_sale category_id brand_id is_new is_hot unit keywords brief detail",
        "category_id → mal_category.id；brand_id → mal_brand.id"),
    "mal_goods_specification": TableAccess("商品规格", "goods:query",
        "goods_id name value", "goods_id → mal_goods.id"),
    "mal_goods_product": TableAccess("商品货品库存", "goods:query",
        "goods_id specification price quantity", "goods_id → mal_goods.id"),
    "mal_goods_attribute": TableAccess("商品参数", "goods:query",
        "goods_id name value", "goods_id → mal_goods.id"),
    "mal_goods_comment": TableAccess("商品评论", "goodsComment:query",
        "goods_id member_id username score content comment_time reply_content reply_time",
        "goods_id → mal_goods.id；member_id → mal_member.id"),
    "mal_brand": TableAccess("品牌", "brand:query", "name description floor_price"),
    "mal_category": TableAccess("商品分类", "category:query",
        "name parent_id level keywords description", "parent_id → mal_category.id"),
    "mal_member": TableAccess("商城会员账号", "member:query", "username nickname status level gender"),
    "mal_address": TableAccess("会员收货地址", "address:query",
        "member_id region is_default", "member_id → mal_member.id"),
    "mal_order": TableAccess("商城订单", "order:query",
        "order_no username member_id status order_time total_amount pay_amount pay_time pay_channel goods_amount "
        "freight_amount discount_amount coupon_user_id express_company deliver_time confirm_time refund_amount "
        "refund_type refund_time",
        "member_id → mal_member.id（订单 username 是下单昵称快照；会员 username 是登录账号）；"
        "coupon_user_id → mal_coupon_user.id"),
    "mal_order_item": TableAccess("订单商品明细", "order:query",
        "order_id goods_id goods_name goods_no spec price quantity product_id",
        "order_id → mal_order.id；goods_id → mal_goods.id；product_id → mal_goods_product.id"),
    "mal_after_sale": TableAccess("售后及退款申请", "afterSale:query",
        "after_sale_no order_no order_id username member_id type refund_amount status apply_time audit_time",
        "order_id → mal_order.id；member_id → mal_member.id"),
    "mal_cart": TableAccess("会员购物车", SUPER_ADMIN_ONLY,
        "member_id goods_id product_id quantity checked",
        "member_id → mal_member.id；goods_id → mal_goods.id；product_id → mal_goods_product.id"),
    "mal_favorite": TableAccess("会员收藏", "favorite:query",
        "member_id goods_id", "member_id → mal_member.id；goods_id → mal_goods.id"),
    "mal_footprint": TableAccess("会员足迹", "footprint:query",
        "member_id goods_id", "member_id → mal_member.id；goods_id → mal_goods.id"),
    "mal_search_history": TableAccess("会员搜索历史", "searchHistory:query",
        "member_id keyword", "member_id → mal_member.id"),
    "mal_feedback": TableAccess("会员反馈", "feedback:query",
        "member_id username feedback_type content", "member_id → mal_member.id"),
    "mal_ad": TableAccess("商城广告", "ad:query", "title position status content"),
    "mal_faq": TableAccess("常见问题", "faq:query", "question answer"),
    "mal_keyword": TableAccess("商城关键词", "keyword:query", "keyword is_recommend is_default"),
    "mal_region": TableAccess("行政区划", "", "name code parent_id level sort", "parent_id → mal_region.id"),
    "mal_coupon": TableAccess("优惠券", "coupon:query",
        "name status effective_status discount min total type time_type days start_time end_time goods_type tag "
        "description limit"),
    "mal_coupon_category": TableAccess("优惠券适用分类", "coupon:query",
        "coupon_id category_id", "coupon_id → mal_coupon.id；category_id → mal_category.id"),
    "mal_coupon_goods": TableAccess("优惠券适用商品", "coupon:query",
        "coupon_id goods_id", "coupon_id → mal_coupon.id；goods_id → mal_goods.id"),
    "mal_coupon_user": TableAccess("会员领券和核销记录", "coupon:query",
        "coupon_id user_id status effective_status order_id receive_time use_time start_time end_time",
        "coupon_id → mal_coupon.id；user_id → mal_member.id；order_id → mal_order.id"),
    "mal_topic": TableAccess("商城专题", "topic:query", "title subtitle price read_count content"),
    "mal_topic_goods": TableAccess("专题商品", "topic:query",
        "topic_id goods_id sort", "topic_id → mal_topic.id；goods_id → mal_goods.id"),
    "mal_group_rule": TableAccess("团购规则", "groupRule:query",
        "goods_id discount people end_time", "goods_id → mal_goods.id"),
    "mal_group_activity": TableAccess("团购活动", "groupActivity:query",
        "rule_id member_id order_id participants people discount start_time end_time",
        "rule_id → mal_group_rule.id；member_id → mal_member.id；order_id → mal_order.id"),
    "mal_group_activity_member": TableAccess("团购参团记录", "groupActivity:query",
        "activity_id order_id member_id join_time",
        "activity_id → mal_group_activity.id；order_id → mal_order.id；member_id → mal_member.id"),
    "sys_user": TableAccess("后台管理员账号", "user:query",
        "username nickname status user_type dept_id", "dept_id → sys_dept.id"),
    "sys_dept": TableAccess("部门", "", "name parent_id sort status description", "parent_id → sys_dept.id"),
    "sys_role": TableAccess("后台角色", "role:query",
        "name role_type status data_scope dept_id description", "dept_id → sys_dept.id"),
    "sys_user_role": TableAccess("后台用户角色关系", "user:query",
        "user_id role_id", "user_id → sys_user.id；role_id → sys_role.id"),
    "sys_role_menu": TableAccess("角色菜单关系", "role:query",
        "role_id menu_id", "role_id → sys_role.id；menu_id → sys_menu.id"),
    "sys_role_dept": TableAccess("角色部门权限关系", "role:query",
        "role_id dept_id", "role_id → sys_role.id；dept_id → sys_dept.id"),
    "sys_menu": TableAccess("后台菜单", "", "name title parent_id menu_type sort views", "parent_id → sys_menu.id"),
    "sys_menu_view_history": TableAccess("后台菜单访问记录", SUPER_ADMIN_ONLY,
        "menu_id user_id", "menu_id → sys_menu.id；user_id → sys_user.id"),
    "sys_dict_type": TableAccess("数据字典类型", "", "code description"),
    "sys_dict_data": TableAccess("数据字典值", "",
        "lookup_id lookup_code lookup_value display_sequence", "lookup_id → sys_dict_type.id"),
    "sys_login_record": TableAccess("后台登录日志", "loginRecord:query",
        "user_id user_name login_type login_time logout_time logout_type ret_code source_type",
        "user_id → sys_user.id"),
    "sys_operation_log": TableAccess("后台操作日志", "operationLog:query",
        "user_id username request_method response_code process_time status", "user_id → sys_user.id"),
    "sys_file": TableAccess("后台文件记录", SUPER_ADMIN_ONLY,
        "name original_name extend_name content_type file_size storage_type uploader_id uploader_name",
        "uploader_id → sys_user.id"),
    "celery_periodic_task": TableAccess("定时任务", SUPER_ADMIN_ONLY,
        "name task_type enabled start_time expires one_off last_run_at total_run_count date_changed crontab_id "
        "interval_id", "crontab_id → celery_crontab_schedule.id；interval_id → celery_interval_schedule.id"),
    "celery_crontab_schedule": TableAccess("定时任务时间表", SUPER_ADMIN_ONLY,
        "minute hour day_of_week day_of_month month_of_year timezone"),
    "celery_interval_schedule": TableAccess("定时任务间隔", SUPER_ADMIN_ONLY, "every period"),
    "celery_periodic_task_changed": TableAccess("定时任务更新时间", SUPER_ADMIN_ONLY, "last_update"),
    SOLAR_SCHEDULE: TableAccess("定时任务日出日落计划", SUPER_ADMIN_ONLY, "event"),
}
