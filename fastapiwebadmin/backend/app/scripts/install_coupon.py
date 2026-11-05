# -*- coding: utf-8 -*-
"""幂等安装优惠券管理/详情菜单并初始化示例数据：python -m app.scripts.install_coupon。"""

import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.category.model import Category
from app.api.v1.system.coupon.model import Coupon, CouponCategory, CouponGoods
from app.api.v1.system.goods.model import Goods
from app.api.v1.system.menu.model import Menu
from app.api.v1.system.roles.model import RoleMenu, Roles
from app.database.database import create_tables
from app.database.sqlalchemy import async_session_factory, engine


async def _seed_coupons(session: AsyncSession) -> int:
    """仅在优惠券表完全为空时预置示例，不修改已有优惠券。"""
    count = await session.scalar(select(func.count()).select_from(Coupon))
    if count:
        return 0

    category_id = await session.scalar(
        select(Category.id)
        .where(Category.enabled_flag.is_(True))
        .order_by(Category.level.desc(), Category.id.asc())
        .limit(1)
    )
    goods_id = await session.scalar(
        select(Goods.id)
        .where(Goods.enabled_flag.is_(True))
        .order_by(Goods.id.asc())
        .limit(1)
    )
    now = datetime.now().replace(microsecond=0)
    examples = [
        {
            "name": "限时满减券3",
            "description": "全场通用",
            "tag": "限量发行",
            "min": Decimal("10.00"),
            "discount": Decimal("3.00"),
            "limit": 1,
            "type": 0,
            "total": 1,
            "time_type": 0,
            "days": 7,
            "goods_type": 0,
        },
        {
            "name": "限时满减券3",
            "description": "全场通用",
            "tag": "无限制",
            "min": Decimal("99.00"),
            "discount": Decimal("20.00"),
            "limit": 3,
            "type": 0,
            "total": 0,
            "time_type": 1,
            "days": 0,
            "start_time": now,
            "end_time": now + timedelta(days=30),
            "goods_type": 0,
        },
        {
            "name": "可兑换优惠券",
            "description": "全场通用",
            "tag": "仅兑换领券",
            "min": Decimal("99.00"),
            "discount": Decimal("15.00"),
            "limit": 10,
            "type": 2,
            "total": 0,
            "time_type": 0,
            "days": 30,
            "goods_type": 0,
        },
        {
            "name": "限时满减券1",
            "description": "全场通用",
            "tag": "无限制",
            "min": Decimal("99.00"),
            "discount": Decimal("5.00"),
            "limit": 2,
            "type": 0,
            "total": 0,
            "time_type": 0,
            "days": 14,
            "goods_type": 0,
        },
        {
            "name": "限时满减券2",
            "description": "指定分类可用" if category_id else "全场通用",
            "tag": "分类专享" if category_id else "无限制",
            "min": Decimal("99.00"),
            "discount": Decimal("10.00"),
            "limit": 10,
            "type": 0,
            "total": 0,
            "time_type": 1,
            "days": 0,
            "start_time": now,
            "end_time": now + timedelta(days=30),
            "goods_type": 1 if category_id else 0,
        },
        {
            "name": "新用户优惠券",
            "description": "指定商品可用" if goods_id else "全场通用",
            "tag": "新人专享",
            "min": Decimal("99.00"),
            "discount": Decimal("10.00"),
            "limit": 1,
            "type": 1,
            "total": 0,
            "time_type": 0,
            "days": 30,
            "goods_type": 2 if goods_id else 0,
        },
    ]

    for values in examples:
        coupon = Coupon(**values, status=0)
        session.add(coupon)
        await session.flush()
        if values["goods_type"] == 1:
            session.add(CouponCategory(coupon_id=coupon.id, category_id=category_id))
        elif values["goods_type"] == 2:
            session.add(CouponGoods(coupon_id=coupon.id, goods_id=goods_id))
    return len(examples)


async def install() -> None:
    """创建缺失表、安装管理与详情菜单权限，并在空表中建立六条示例。"""
    await create_tables()
    json_path = Path(__file__).parent / "data" / "sys_menu.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    root = next((item for item in data if item["path"] == "/promotion"), None)
    if root is None:
        raise ValueError("初始化数据中缺少推广管理菜单")
    coupon_menu = next(
        (item for item in root.get("children", []) if item["path"] == "/promotion/coupon"),
        None,
    )
    if coupon_menu is None:
        raise ValueError("初始化数据中缺少优惠券管理菜单")
    detail_menu = next(
        (item for item in root.get("children", []) if item["path"] == "/promotion/couponDetail"),
        None,
    )
    if detail_menu is None:
        raise ValueError("初始化数据中缺少优惠券详情菜单")

    # 仅同步推广管理根节点、优惠券管理与隐藏详情页，不改动广告等其他推广模块。
    root = {**root, "children": [coupon_menu, detail_menu]}
    async with async_session_factory() as session:
        async with session.begin():
            menu_ids = []

            async def upsert(item, parent_id=0):
                values = {key: value for key, value in item.items() if key != "children"}
                values.setdefault("isLink", 0)
                values.setdefault("isHide", 0)
                values.setdefault("isKeepAlive", 1)
                values.setdefault("isAffix", 0)
                values.setdefault("isIframe", 0)
                condition = (
                    Menu.roles == values["roles"]
                    if values.get("roles")
                    else Menu.path == values["path"]
                )
                row = await session.scalar(select(Menu).where(condition))
                if row is None:
                    row = Menu(**values, parent_id=parent_id)
                    session.add(row)
                else:
                    for key, value in values.items():
                        setattr(row, key, value)
                    row.parent_id = parent_id
                    row.enabled_flag = True
                await session.flush()
                menu_ids.append(row.id)
                for child in item.get("children", []):
                    await upsert(child, row.id)

            await upsert(root)
            role_id = await session.scalar(
                select(Roles.id).where(Roles.name == "管理员", Roles.enabled_flag.is_(True))
            )
            if role_id:
                for menu_id in menu_ids:
                    if not await session.get(RoleMenu, (role_id, menu_id)):
                        session.add(RoleMenu(role_id=role_id, menu_id=menu_id))
            seeded = await _seed_coupons(session)
    print(f"优惠券表和菜单安装完成，本次新增 {seeded} 条示例优惠券")


if __name__ == "__main__":
    async def main() -> None:
        try:
            await install()
        finally:
            await engine.dispose()

    asyncio.run(main())
