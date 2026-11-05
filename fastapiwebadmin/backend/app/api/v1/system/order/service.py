# -*- coding: utf-8 -*-
"""商城订单业务层"""

import typing
from datetime import datetime
from io import BytesIO
from decimal import Decimal

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from app.api.v1.system.order.model import Order, OrderItem
from app.api.v1.system.order.schema import (
    OrderCollectIn,
    OrderDeliverIn,
    OrderQuery,
    OrderRefundIn,
)

# 订单状态字典
ORDER_STATUS = {
    1: "未付款",
    2: "用户取消",
    3: "系统取消",
    4: "已付款",
    5: "申请退款",
    6: "已退款",
    7: "已发货",
    8: "用户收货",
    9: "系统收货",
}

EXPORT_HEADERS = [
    "订单编号", "下单用户", "下单时间", "订单状态", "订单金额", "实付金额",
    "支付时间", "收货人", "收货电话", "物流单号", "物流渠道",
]


def _parse_time(value: typing.Optional[str]) -> typing.Optional[datetime]:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _money(value) -> float:
    return float(value) if value is not None else 0.0


class OrderService:
    """订单管理"""

    MEMBER_TABS = {"all": (), "pay": (1,), "send": (4,), "receive": (7,), "done": (8, 9)}

    @staticmethod
    async def my_list(params):
        from app.api.v1.system.cart.service import CartService
        from app.database.sqlalchemy import async_session_factory

        member_id = await CartService._member_id()
        async with async_session_factory() as session:
            await CartService._member(session, member_id)
            data = await Order.get_member_list(params, member_id, OrderService.MEMBER_TABS[params.tab])
            items = await OrderItem.get_by_order_ids([row["id"] for row in data["rows"]])
            item_map = {}
            for item in items:
                price = Decimal(str(item.get("price") or 0)).quantize(Decimal("0.01"))
                item_map.setdefault(item["order_id"], []).append({
                    "goods_id": item.get("goods_id"), "product_id": item.get("product_id"),
                    "name": item.get("goods_name") or "", "image": item.get("image") or "",
                    "specification": item.get("spec") or "标准", "quantity": item.get("quantity") or 0,
                    "price": float(price), "price_text": format(price, ".2f"),
                    "subtotal_text": format(price * (item.get("quantity") or 0), ".2f"),
                })
            for row in data["rows"]:
                amount = Decimal(str(row.pop("total_amount") or 0)).quantize(Decimal("0.01"))
                row.update({"status_name": ORDER_STATUS.get(row["status"], "未知"),
                            "order_amount": float(amount), "order_amount_text": format(amount, ".2f"),
                            "items": item_map.get(row["id"], []),
                            "can_pay": row["status"] == 1, "can_delete": row["status"] in (2, 3)})
            return data

    @staticmethod
    async def my_summary():
        from sqlalchemy import func, select
        from app.api.v1.system.cart.service import CartService
        from app.api.v1.system.coupon.model import Coupon, CouponUser
        from app.database.sqlalchemy import async_session_factory

        member_id = await CartService._member_id()
        async with async_session_factory() as session:
            await CartService._member(session, member_id)
            grouped = dict((await session.execute(select(Order.status, func.count(Order.id)).where(
                Order.member_id == member_id, Order.enabled_flag.is_(True)).group_by(Order.status))).all())
            counts = {key: sum(grouped.get(status, 0) for status in statuses) for key, statuses in OrderService.MEMBER_TABS.items()}
            counts["all"] = sum(grouped.values())
            # 与「我的优惠券」同一套口径：绝对有效期券跟着券定义走，后台改期立即生效
            from datetime import datetime
            from app.api.v1.system.coupon.service import CouponService

            pairs = (await session.execute(
                select(CouponUser, Coupon).join(Coupon, Coupon.id == CouponUser.coupon_id)
                .where(CouponUser.user_id == member_id, CouponUser.enabled_flag.is_(True))
            )).all()
            coupon_counts = {0: 0, 1: 0, 2: 0}
            now = datetime.now()
            for user_coupon, coupon in pairs:
                coupon_counts[CouponService._effective_status(user_coupon, coupon, now)] += 1
            return {"counts": counts, "coupon_counts": {
                "unused": coupon_counts[0], "used": coupon_counts[1], "expired": coupon_counts[2]}}

    @staticmethod
    async def my_deleted(order_id: int):
        from sqlalchemy import delete, select
        from app.api.v1.system.cart.service import CartService
        from app.database.sqlalchemy import async_session_factory

        member_id = await CartService._member_id()
        async with async_session_factory() as session, session.begin():
            await CartService._member(session, member_id, lock=True)
            order = await session.scalar(select(Order).where(Order.id == order_id, Order.member_id == member_id,
                                                            Order.enabled_flag.is_(True)).with_for_update())
            if not order:
                raise ValueError("订单不存在或不属于当前用户")
            if order.status not in (2, 3):
                raise ValueError("仅可删除已取消的订单")
            # 删除历史展示记录不执行取消动作，不重复恢复库存或释放优惠券。
            await session.execute(delete(OrderItem).where(OrderItem.order_id == order.id))
            await session.execute(delete(Order).where(Order.id == order.id))
            return {}

    @staticmethod
    def _decorate(order: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        order["status_name"] = ORDER_STATUS.get(order.get("status"), "未知")
        order["total_amount"] = _money(order.get("total_amount"))
        order["pay_amount"] = _money(order.get("pay_amount"))
        if order.get("refund_amount") is not None:
            order["refund_amount"] = _money(order.get("refund_amount"))
        return order

    @staticmethod
    def _decorate_item(item: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        item["price"] = _money(item.get("price"))
        return item

    @staticmethod
    async def list(params: OrderQuery) -> typing.Dict[str, typing.Any]:
        # 时间范围是字符串，转成 datetime 再查
        params.start_time = _parse_time(params.start_time) if isinstance(params.start_time, str) else params.start_time
        params.end_time = _parse_time(params.end_time) if isinstance(params.end_time, str) else params.end_time

        data = await Order.get_list(params)
        rows = data.get("rows", [])
        for row in rows:
            OrderService._decorate(row)

        # 查出本页订单的明细，挂到每条订单下面（供表格展开显示）
        order_ids = [row["id"] for row in rows]
        items = await OrderItem.get_by_order_ids(order_ids)
        item_map: typing.Dict[int, typing.List[typing.Dict[str, typing.Any]]] = {}
        for item in items:
            OrderService._decorate_item(item)
            item_map.setdefault(item["order_id"], []).append(item)
        for row in rows:
            row["items"] = item_map.get(row["id"], [])

        return data

    @staticmethod
    async def detail(order_id: int) -> typing.Dict[str, typing.Any]:
        order = await Order.get(order_id, to_dict=True)
        if not order:
            raise ValueError("订单不存在")
        OrderService._decorate(order)
        items = await OrderItem.get_by_order(order_id)
        order["items"] = [OrderService._decorate_item(item) for item in items]
        return order

    @staticmethod
    async def deleted(order_id: int) -> int:
        from sqlalchemy import select, delete
        from app.database.sqlalchemy import async_session_factory
        from app.api.v1.system.coupon.model import Coupon, CouponUser
        from app.api.v1.system.goods.model import GoodsProduct

        async with async_session_factory() as session, session.begin():
            order = await session.get(Order, order_id)
            if not order:
                raise ValueError("订单不存在")
            if order.checkout_key and order.member_id:
                # 和会员下单使用相同的会员锁，避免删除/重试/用券同时修改。
                from app.api.v1.system.member.model import Member
                await session.scalar(select(Member).where(Member.id == order.member_id).with_for_update())
            order = await session.scalar(select(Order).where(Order.id == order_id).with_for_update().execution_options(populate_existing=True))
            if not order:
                raise ValueError("订单不存在")
            if order.status == 1 and order.checkout_key:
                items = (await session.scalars(select(OrderItem).where(OrderItem.order_id == order.id))).all()
                ids = sorted({item.product_id for item in items if item.product_id})
                products = {row.id: row for row in (await session.scalars(
                    select(GoodsProduct).where(GoodsProduct.id.in_(ids)).order_by(GoodsProduct.id).with_for_update()
                )).all()}
                for item in items:
                    product = products.get(item.product_id)
                    if product:
                        quantity = product.quantity + (item.quantity or 0)
                        if quantity > 2147483647:
                            raise ValueError("库存恢复超出上限，请先调整库存")
                        product.quantity = quantity
                if order.coupon_user_id:
                    coupon_id = await session.scalar(select(CouponUser.coupon_id).where(CouponUser.id == order.coupon_user_id))
                    if coupon_id:
                        await session.scalar(select(Coupon).where(Coupon.id == coupon_id).with_for_update())
                        used = await session.scalar(select(CouponUser).where(CouponUser.id == order.coupon_user_id).with_for_update().execution_options(populate_existing=True))
                        if used and used.order_id == order.id and used.status == 1:
                            used.status, used.order_id, used.use_time = 0, None, None
            await session.execute(delete(OrderItem).where(OrderItem.order_id == order.id))
            await session.execute(delete(Order).where(Order.id == order.id))
            return 1

    # ------------------------------------------------------------------ 暂未实现的业务动作
    @staticmethod
    async def collect(params: OrderCollectIn) -> None:
        """线下收款：当前版本未开放"""
        order = await Order.get(params.id)
        if not order:
            raise ValueError("订单不存在")
        raise ValueError("当前订单状态不支持线下收款")

    @staticmethod
    async def deliver(params: OrderDeliverIn) -> None:
        """发货：当前版本未开放"""
        if not params.express_company or not params.express_no:
            raise ValueError("参数不对")
        order = await Order.get(params.id)
        if not order:
            raise ValueError("订单不存在")
        raise ValueError("订单不能确认收货")

    @staticmethod
    async def refund(params: OrderRefundIn) -> None:
        """退款：当前版本未开放"""
        order = await Order.get(params.id)
        if not order:
            raise ValueError("订单不存在")
        raise ValueError("当前订单不能进行退款")

    # ------------------------------------------------------------------ 导出
    @staticmethod
    async def export(params: OrderQuery) -> tuple[bytes, str]:
        params.start_time = _parse_time(params.start_time) if isinstance(params.start_time, str) else params.start_time
        params.end_time = _parse_time(params.end_time) if isinstance(params.end_time, str) else params.end_time
        rows = await Order.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "订单列表"

        header_fill = PatternFill("solid", fgColor="F2F5F8")
        header_font = Font(bold=True, color="333333")
        center = Alignment(horizontal="center", vertical="center")

        sheet.append(EXPORT_HEADERS)
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center

        for row in rows:
            sheet.append(
                [
                    row.get("order_no") or "",
                    row.get("username") or "",
                    row.get("order_time") or "",
                    ORDER_STATUS.get(row.get("status"), ""),
                    _money(row.get("total_amount")),
                    _money(row.get("pay_amount")),
                    row.get("pay_time") or "",
                    row.get("receiver_name") or "",
                    row.get("receiver_phone") or "",
                    row.get("express_no") or "",
                    row.get("express_company") or "",
                ]
            )

        widths = [20, 14, 20, 10, 12, 12, 20, 10, 16, 18, 12]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"订单列表_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
