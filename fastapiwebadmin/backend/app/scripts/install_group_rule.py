# -*- coding: utf-8 -*-
"""幂等安装团购规则菜单并建立缺失表：python -m app.scripts.install_group_rule。

- 只创建缺失表、同步菜单与管理员绑定，不重置已有数据
- 仅当团购规则表为空时写入几条演示数据（引用当前库真实商品）
"""

import asyncio
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select

from app.api.v1.system.goods.model import Goods
from app.api.v1.system.group_rule.model import GroupRule
from app.api.v1.system.menu.model import Menu
from app.api.v1.system.roles.model import RoleMenu, Roles
from app.database.database import create_tables
from app.database.sqlalchemy import async_session_factory, engine

# (商品序号, 团购优惠, 团购人数, 结束时间)
DEMO = [
    (0, Decimal("20"), 20, datetime(2019, 12, 31, 0, 0, 0)),
    (0, Decimal("50"), 5, datetime(2027, 12, 31, 0, 0, 0)),
    (1, Decimal("29"), 2, datetime(2022, 3, 29, 0, 0, 0)),
    (1, Decimal("39"), 2, datetime(2020, 12, 31, 0, 0, 0)),
    (2, Decimal("400"), 2, datetime(2022, 4, 11, 0, 0, 0)),
]


async def install() -> None:
    """创建缺失表、同步推广管理菜单、绑定管理员，并按需写入演示规则。"""
    await create_tables()
    json_path = Path(__file__).parent / "data" / "sys_menu.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    root = next((item for item in data if item["path"] == "/promotion"), None)
    if root is None:
        raise ValueError("初始化数据中缺少推广管理菜单")

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

            count = await session.scalar(select(func.count()).select_from(GroupRule))
            if count:
                print(f"团购规则表已有 {count} 条数据，跳过演示数据")
            else:
                goods_ids = (
                    await session.scalars(select(Goods.id).order_by(Goods.id.asc()).limit(3))
                ).all()
                if not goods_ids:
                    print("当前没有商品，跳过演示数据")
                else:
                    added = 0
                    for index, discount, people, end_time in DEMO:
                        if index >= len(goods_ids):
                            continue
                        session.add(
                            GroupRule(
                                goods_id=goods_ids[index],
                                discount=discount,
                                people=people,
                                end_time=end_time,
                                enabled_flag=True,
                            )
                        )
                        added += 1
                    print(f"写入 {added} 条演示团购规则")

    print("团购规则表和菜单安装完成")


if __name__ == "__main__":
    async def main() -> None:
        try:
            await install()
        finally:
            await engine.dispose()

    asyncio.run(main())
