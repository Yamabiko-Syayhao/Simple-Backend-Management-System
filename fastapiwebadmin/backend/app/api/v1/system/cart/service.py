# -*- coding: utf-8 -*-
"""购物车业务层：会员隔离、实时售价/库存及勾选金额计算。"""

import typing
from decimal import Decimal

from sqlalchemy import delete, func, select

from app.api.v1.system.cart.model import Cart
from app.api.v1.system.cart.schema import CartChecked, CartDel, CartIn, CartUpdate
from app.api.v1.system.goods.model import Goods, GoodsProduct
from app.api.v1.system.member.model import Member
from app.database.sqlalchemy import async_session_factory
from app.shared.exceptions import AccessTokenFail
from app.utils.current_user import current_user


class CartService:
    @staticmethod
    async def _member_id() -> int:
        user = await current_user()
        if not user or not user.get("member_id") or user.get("id"):
            raise AccessTokenFail()
        return int(user["member_id"])

    @staticmethod
    async def _member(session, member_id: int, lock: bool = False):
        stmt = select(Member).where(Member.id == member_id)
        if lock:
            # 同一会员的写操作串行，避免两个请求重复创建或丢失数量累加。
            stmt = stmt.with_for_update()
        member = await session.scalar(stmt)
        if not member or not member.enabled_flag or member.status != 1:
            raise AccessTokenFail()
        return member

    @staticmethod
    def _invalid_reason(cart, goods, product) -> str:
        if not goods or not goods.enabled_flag:
            return "商品已删除"
        if not goods.is_on_sale:
            return "商品已下架"
        if not product or not product.enabled_flag or product.goods_id != goods.id:
            return "商品规格已失效"
        if product.quantity <= 0:
            return "商品已售罄"
        if cart.quantity > product.quantity:
            return "库存不足，请调整数量"
        return ""

    @staticmethod
    def _decorate(cart, goods, product) -> typing.Dict[str, typing.Any]:
        reason = CartService._invalid_reason(cart, goods, product)
        price = Decimal(product.price or 0) if product else Decimal("0")
        subtotal = price * cart.quantity
        return {
            "id": cart.id,
            "goods_id": cart.goods_id,
            "product_id": cart.product_id,
            "name": goods.name if goods else "商品已删除",
            "goods_sn": goods.goods_sn if goods else "",
            "image": ((product.image if product else "") or (goods.image if goods else "") or ""),
            "specification": product.specification if product else "规格已删除",
            "price": float(price),
            "price_text": format(price, ".2f"),
            "quantity": cart.quantity,
            "stock": max(int(product.quantity or 0), 0) if product else 0,
            # 失效商品即使此前选中也不参与本次合计，不在读取时修改数据库。
            "checked": bool(cart.checked and not reason),
            "available": not bool(reason),
            "invalid_reason": reason,
            "subtotal": float(subtotal),
            "subtotal_text": format(subtotal, ".2f"),
            "creation_date": cart.creation_date.strftime("%Y-%m-%d %H:%M:%S") if cart.creation_date else "",
        }

    @staticmethod
    async def _summary(session, member_id: int) -> typing.Dict[str, typing.Any]:
        rows = [CartService._decorate(*row) for row in await Cart.get_list(member_id, session)]
        selected = [row for row in rows if row["checked"] and row["available"]]
        amount = sum((Decimal(row["subtotal_text"]) for row in selected), Decimal("0"))
        return {
            "rows": rows,
            "rowTotal": len(rows),
            "total_quantity": sum(row["quantity"] for row in rows),
            "selected_quantity": sum(row["quantity"] for row in selected),
            "selected_count": len(selected),
            "total_amount": float(amount),
            "total_amount_text": format(amount, ".2f"),
        }

    @staticmethod
    async def list() -> typing.Dict[str, typing.Any]:
        member_id = await CartService._member_id()
        async with async_session_factory() as session:
            await CartService._member(session, member_id)
            return await CartService._summary(session, member_id)

    @staticmethod
    async def _product(session, goods_id: int, product_id: int, lock: bool = True):
        goods_stmt = select(Goods).where(Goods.id == goods_id)
        if lock:
            goods_stmt = goods_stmt.with_for_update()
        goods = await session.scalar(goods_stmt)
        if not goods or not goods.enabled_flag:
            raise ValueError("商品不存在或已删除")
        if not goods.is_on_sale:
            raise ValueError("商品已下架，暂时无法加入购物车")
        product_stmt = select(GoodsProduct).where(GoodsProduct.id == product_id)
        if lock:
            product_stmt = product_stmt.with_for_update()
        product = await session.scalar(product_stmt)
        if not product or not product.enabled_flag or product.goods_id != goods_id:
            raise ValueError("商品规格不存在或不属于该商品")
        return goods, product

    @staticmethod
    def _check_quantity(quantity: int, product):
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1 or quantity > 999:
            raise ValueError("购买数量应为1至999的整数")
        if quantity > product.quantity:
            raise ValueError("商品库存不足，请调整数量")

    @staticmethod
    async def add(params: CartIn) -> typing.Dict[str, typing.Any]:
        member_id = await CartService._member_id()
        async with async_session_factory() as session, session.begin():
            await CartService._member(session, member_id, lock=True)
            _, product = await CartService._product(session, params.goods_id, params.product_id)
            cart = await session.scalar(
                select(Cart).where(Cart.member_id == member_id, Cart.product_id == params.product_id).with_for_update()
            )
            quantity = params.quantity + (cart.quantity if cart and cart.enabled_flag else 0)
            CartService._check_quantity(quantity, product)
            if cart:
                cart.goods_id = params.goods_id
                cart.quantity = quantity
                cart.checked = True
                cart.enabled_flag = True
            else:
                payload = await Cart.handle_params({
                    "member_id": member_id, "goods_id": params.goods_id,
                    "product_id": params.product_id, "quantity": quantity, "checked": True,
                })
                cart = Cart(**payload)
                session.add(cart)
            await session.flush()
            return await CartService._summary(session, member_id)

    @staticmethod
    async def _own_rows(session, member_id: int, ids: typing.List[int], lock: bool = True):
        unique_ids = sorted(set(ids))
        if not unique_ids or any(i <= 0 for i in unique_ids):
            raise ValueError("请选择至少一条购物车记录")
        stmt = select(Cart).where(
            Cart.member_id == member_id, Cart.id.in_(unique_ids), Cart.enabled_flag.is_(True)
        ).order_by(Cart.id)
        if lock:
            stmt = stmt.with_for_update()
        rows = (await session.scalars(stmt)).all()
        if len(rows) != len(unique_ids):
            raise ValueError("部分购物车记录不存在，请刷新后重试")
        return rows

    @staticmethod
    async def update(params: CartUpdate) -> typing.Dict[str, typing.Any]:
        member_id = await CartService._member_id()
        async with async_session_factory() as session, session.begin():
            await CartService._member(session, member_id, lock=True)
            cart = (await CartService._own_rows(session, member_id, [params.id], lock=False))[0]
            _, product = await CartService._product(session, cart.goods_id, cart.product_id)
            CartService._check_quantity(params.quantity, product)
            # 与加入购物车一致：商品 -> 库存 -> 购物车，避免与后台删除商品反向持锁。
            cart = (await CartService._own_rows(session, member_id, [params.id]))[0]
            cart.quantity = params.quantity
            await session.flush()
            return await CartService._summary(session, member_id)

    @staticmethod
    async def checked(params: CartChecked) -> typing.Dict[str, typing.Any]:
        member_id = await CartService._member_id()
        async with async_session_factory() as session, session.begin():
            await CartService._member(session, member_id, lock=True)
            rows = await CartService._own_rows(session, member_id, params.ids)
            for cart in rows:
                if params.checked:
                    # 勾选不预占库存，不对跨商品记录逐个加锁，避免多商品全选的交叉锁。
                    goods, product = await CartService._product(session, cart.goods_id, cart.product_id, lock=False)
                    reason = CartService._invalid_reason(cart, goods, product)
                    if reason:
                        raise ValueError(reason)
                cart.checked = params.checked
            await session.flush()
            return await CartService._summary(session, member_id)

    @staticmethod
    async def deleted(params: CartDel) -> typing.Dict[str, typing.Any]:
        member_id = await CartService._member_id()
        async with async_session_factory() as session, session.begin():
            await CartService._member(session, member_id, lock=True)
            rows = await CartService._own_rows(session, member_id, params.ids)
            # 真正删除购物车条目，不删除商品、库存或其他会员的购物车。
            await session.execute(delete(Cart).where(Cart.member_id == member_id, Cart.id.in_([row.id for row in rows])))
            await session.flush()
            return await CartService._summary(session, member_id)

    @staticmethod
    async def count() -> typing.Dict[str, int]:
        member_id = await CartService._member_id()
        async with async_session_factory() as session:
            await CartService._member(session, member_id)
            count = await session.scalar(select(func.coalesce(func.sum(Cart.quantity), 0)).where(
                Cart.member_id == member_id, Cart.enabled_flag.is_(True)
            ))
            return {"count": int(count or 0)}
