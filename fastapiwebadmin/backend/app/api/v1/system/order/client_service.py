"""会员结算业务；库存、订单明细、用券和购物车清理在同一事务中完成。"""
import hashlib
import json
import re
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select

from app.api.v1.system.address.model import Address
from app.api.v1.system.address.service import AddressService
from app.api.v1.system.cart.model import Cart
from app.api.v1.system.cart.service import CartService
from app.api.v1.system.coupon.service import CouponService
from app.api.v1.system.goods.model import Goods, GoodsProduct
from app.api.v1.system.order.model import Order, OrderItem
from app.api.v1.system.order.schema import CheckoutPreview
from app.api.v1.system.order.service import ORDER_STATUS
from app.database import redis_pool
from app.database.sqlalchemy import async_session_factory

ZERO = Decimal("0.00")
FREIGHT_THRESHOLD = Decimal("88.00")
FREIGHT_FEE = Decimal("80.00")
QUOTE_TTL = 900
QUOTE_KEY = "fastapiwebadmin:checkout_quote:{}"
PAYMENT_METHODS = [
    {"code": code, "name": name, "short_name": short, "color": color}
    for code, name, short, color in [
        ("wechat", "微信支付", "微", "#20ad52"), ("alipay", "支付宝", "支", "#159fee"),
        ("visa", "Visa", "VISA", "#173e8c"), ("mastercard", "Mastercard 万事达", "MC", "#df492c"),
        ("paypay", "PayPay", "P", "#ef3043"), ("paypal", "PayPal", "PP", "#1265ab"),
        ("apple_pay", "Apple Pay", "Pay", "#222222"), ("google_pay", "Google Pay", "G", "#4285f4"),
        ("unionpay", "银联支付", "银", "#137a79"), ("jcb", "JCB", "JCB", "#176ba3"),
        ("amex", "American Express 美国运通", "AMEX", "#2474a8"),
        ("discover", "Discover", "D", "#ec7b22"), ("rakuten_pay", "楽天ペイ Rakuten Pay", "R", "#bc1730"),
        ("amazon_pay", "Amazon Pay", "a", "#e59120"), ("alipay_hk", "AlipayHK", "HK", "#128bce"),
    ]
]


def money(value):
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


class CheckoutService:
    @staticmethod
    async def _lines(session, member_id, params, lock=False):
        if params.source == "cart":
            carts = await CartService._own_rows(session, member_id, params.cart_ids, lock=False)
            selections = [{"goods_id": c.goods_id, "product_id": c.product_id, "quantity": c.quantity, "cart_id": c.id} for c in carts]
        else:
            selections = [{"goods_id": params.goods_id, "product_id": params.product_id, "quantity": params.quantity, "cart_id": None}]
        goods_ids = sorted({row["goods_id"] for row in selections if row["goods_id"]})
        product_ids = sorted({row["product_id"] for row in selections if row["product_id"]})
        goods_stmt = select(Goods).where(Goods.id.in_(goods_ids)).order_by(Goods.id)
        product_stmt = select(GoodsProduct).where(GoodsProduct.id.in_(product_ids)).order_by(GoodsProduct.id)
        if lock:
            goods_stmt, product_stmt = goods_stmt.with_for_update(), product_stmt.with_for_update()
        goods_map = {row.id: row for row in (await session.scalars(goods_stmt)).all()}
        product_map = {row.id: row for row in (await session.scalars(product_stmt)).all()}
        result = []
        for selected in selections:
            goods, product = goods_map.get(selected["goods_id"]), product_map.get(selected["product_id"])
            if not goods or not goods.enabled_flag or not goods.is_on_sale:
                raise ValueError("结算商品不存在或已下架，请返回重新选择")
            if not product or not product.enabled_flag or product.goods_id != goods.id:
                raise ValueError("结算商品规格已失效，请重新选择")
            CartService._check_quantity(selected["quantity"], product)
            price = money(product.price)
            if price < ZERO:
                raise ValueError("商品价格异常")
            result.append({**selected, "name": goods.name, "goods_sn": goods.goods_sn or "",
                           "category_id": goods.category_id, "image": product.image or goods.image or "",
                           "specification": product.specification or "标准", "price": price,
                           "subtotal": price * selected["quantity"]})
        if lock and params.source == "cart":
            await CartService._own_rows(session, member_id, params.cart_ids, lock=True)
        return result, product_map

    @staticmethod
    async def _address(session, member_id, address_id=None, lock=False):
        stmt = select(Address).where(Address.member_id == member_id, Address.enabled_flag.is_(True))
        if address_id:
            stmt = stmt.where(Address.id == address_id)
        stmt = stmt.order_by(Address.is_default.desc(), Address.id).limit(1)
        if lock:
            stmt = stmt.with_for_update()
        row = await session.scalar(stmt)
        if address_id and not row:
            raise ValueError("收货地址不存在或不属于当前用户")
        return row

    @staticmethod
    async def _calculate(session, member_id, params, lock=False):
        lines, products = await CheckoutService._lines(session, member_id, params, lock)
        address = await CheckoutService._address(session, member_id, params.address_id, lock)
        goods_amount = sum((row["subtotal"] for row in lines), ZERO)
        freight = ZERO if goods_amount >= FREIGHT_THRESHOLD else FREIGHT_FEE
        discount, user_coupon = ZERO, None
        if params.coupon_user_id:
            user_coupon, discount = await CouponService.validate_order_coupon(
                session, member_id, params.coupon_user_id, lines, lock=lock
            )
        amount = goods_amount + freight - discount
        if amount < ZERO or amount > Decimal("9999999999.99"):
            raise ValueError("订单金额超出允许范围")
        return lines, products, address, user_coupon, goods_amount, freight, discount, amount

    @staticmethod
    def _items(lines):
        return [{**{key: row[key] for key in ("goods_id", "product_id", "name", "image", "specification", "quantity")},
                 "price": float(row["price"]), "price_text": format(row["price"], ".2f"),
                 "subtotal": float(row["subtotal"]), "subtotal_text": format(row["subtotal"], ".2f")}
                for row in lines]

    @staticmethod
    def _fingerprint(calculated):
        lines, _, address, coupon, goods, freight, discount, amount = calculated
        snapshot = {"items": lines, "address": AddressService.client_row(address) if address else None,
                    "coupon_user_id": coupon.id if coupon else None,
                    "amounts": [str(value) for value in (goods, freight, discount, amount)]}
        return hashlib.sha256(json.dumps(snapshot, sort_keys=True, default=str, ensure_ascii=False).encode()).hexdigest()

    @staticmethod
    async def _quote(member_id, quote_token):
        quote = await redis_pool.redis.get(QUOTE_KEY.format(quote_token))
        if not quote or quote.get("member_id") != member_id:
            raise ValueError("结算信息已过期，请刷新后重新确认")
        return quote

    @staticmethod
    async def preview(params):
        member_id = await CartService._member_id()
        async with async_session_factory() as session:
            await CartService._member(session, member_id)
            calculated = await CheckoutService._calculate(session, member_id, params)
            lines, _, address, coupon, goods, freight, discount, amount = calculated
            quote_token = uuid4().hex
            selection = params.model_dump()
            if address:
                selection["address_id"] = address.id
            await redis_pool.redis.set(QUOTE_KEY.format(quote_token), {
                "member_id": member_id, "selection": selection,
                "fingerprint": CheckoutService._fingerprint(calculated),
            }, QUOTE_TTL)
            result = {"quote_token": quote_token, "items": CheckoutService._items(lines),
                      "address": AddressService.client_row(address) if address else None,
                      "coupon_user_id": coupon.id if coupon else None,
                      "coupons": await CouponService.order_coupons(session, member_id, lines),
                      "freight_rule": "满88元免运费，不满收80元"}
            for key, value in (("goods_amount", goods), ("freight_amount", freight), ("discount_amount", discount), ("order_amount", amount)):
                result[key], result[key + "_text"] = float(value), format(value, ".2f")
            return result

    @staticmethod
    async def coupons(params):
        member_id = await CartService._member_id()
        quote = await CheckoutService._quote(member_id, params.quote_token)
        async with async_session_factory() as session:
            await CartService._member(session, member_id)
            selection = CheckoutPreview(**quote["selection"])
            lines, _ = await CheckoutService._lines(session, member_id, selection)
            return {"rows": await CouponService.order_coupons(session, member_id, lines)}

    @staticmethod
    async def submit(params):
        member_id = await CartService._member_id()
        async with async_session_factory() as session, session.begin():
            member = await CartService._member(session, member_id, lock=True)
            existing = await session.scalar(select(Order).where(Order.member_id == member_id, Order.checkout_key == params.request_key))
            if existing:
                return await CheckoutService._order_row(session, existing)
            quote = await CheckoutService._quote(member_id, params.quote_token)
            selection = CheckoutPreview(**quote["selection"])
            calculated = await CheckoutService._calculate(session, member_id, selection, lock=True)
            lines, products, address, coupon, goods, freight, discount, amount = calculated
            if not address:
                raise ValueError("请先添加并选择收货地址")
            if not re.fullmatch(r"1[3-9]\d{9}", address.mobile or "") or not address.receiver_name or not address.region or not address.detail:
                raise ValueError("收货地址信息不完整，请先编辑地址")
            if quote["fingerprint"] != CheckoutService._fingerprint(calculated):
                raise ValueError("价格、地址或优惠信息已变化，请重新确认订单")
            now = datetime.now().replace(microsecond=0)
            order = Order(order_no=now.strftime("%Y%m%d%H%M%S") + uuid4().hex[:16], member_id=member_id,
                          username=member.nickname or member.username, avatar=member.avatar,
                          order_time=now, status=1, total_amount=amount, pay_amount=ZERO,
                          goods_amount=goods, freight_amount=freight, discount_amount=discount,
                          coupon_user_id=coupon.id if coupon else None, checkout_key=params.request_key,
                          user_message=(params.user_message or "").strip(), receiver_name=address.receiver_name,
                          receiver_phone=address.mobile, receiver_region=address.region, receiver_detail=address.detail)
            session.add(order)
            await session.flush()
            for row in lines:
                products[row["product_id"]].quantity -= row["quantity"]
                session.add(OrderItem(order_id=order.id, goods_id=row["goods_id"], product_id=row["product_id"],
                                      goods_name=row["name"], goods_no=row["goods_sn"], spec=row["specification"],
                                      price=row["price"], quantity=row["quantity"], image=row["image"]))
            if coupon:
                coupon.status, coupon.order_id, coupon.use_time = 1, order.id, now
            if selection.source == "cart":
                await session.execute(delete(Cart).where(Cart.member_id == member_id, Cart.id.in_(selection.cart_ids)))
            await session.flush()
            result = await CheckoutService._order_row(session, order)
            # 报价只允许提交一次。持有会员锁时先消费临时报价，再提交事务；
            # 后续同 request_key 从订单返回结果，不同 key 不能重放旧报价。
            # Redis 失败会回滚本次数据库写入；提交失败则重新报价即可。
            await redis_pool.redis.delete(QUOTE_KEY.format(params.quote_token))
            return result

    @staticmethod
    async def _order_row(session, order):
        rows = (await session.scalars(select(OrderItem).where(OrderItem.order_id == order.id, OrderItem.enabled_flag.is_(True)).order_by(OrderItem.id))).all()
        items = [{"goods_id": row.goods_id, "product_id": row.product_id, "name": row.goods_name,
                  "image": row.image or "", "specification": row.spec or "标准", "quantity": row.quantity,
                  "price": float(money(row.price)), "price_text": format(money(row.price), ".2f"),
                  "subtotal_text": format(money(row.price) * (row.quantity or 0), ".2f")} for row in rows]
        goods = money(order.goods_amount) if order.goods_amount is not None else sum((money(row.price) * (row.quantity or 0) for row in rows), ZERO)
        result = {"id": order.id, "order_no": order.order_no, "status": order.status,
                  "status_name": ORDER_STATUS.get(order.status, "未知"), "items": items,
                  "address": {"receiver_name": order.receiver_name, "mobile": order.receiver_phone,
                              "region": order.receiver_region, "detail": order.receiver_detail},
                  "coupon_user_id": order.coupon_user_id, "user_message": order.user_message or "",
                  "order_time": order.order_time.strftime("%Y-%m-%d %H:%M:%S") if order.order_time else None,
                  "payment_methods": PAYMENT_METHODS, "payment_placeholder": True}
        for key, value in (("goods_amount", goods), ("freight_amount", money(order.freight_amount)),
                           ("discount_amount", money(order.discount_amount)), ("order_amount", money(order.total_amount))):
            result[key], result[key + "_text"] = float(value), format(value, ".2f")
        return result

    @staticmethod
    async def my_detail(order_id):
        member_id = await CartService._member_id()
        async with async_session_factory() as session:
            await CartService._member(session, member_id)
            order = await session.scalar(select(Order).where(Order.id == order_id, Order.member_id == member_id, Order.enabled_flag.is_(True)))
            if not order:
                raise ValueError("订单不存在或不属于当前用户")
            return await CheckoutService._order_row(session, order)
