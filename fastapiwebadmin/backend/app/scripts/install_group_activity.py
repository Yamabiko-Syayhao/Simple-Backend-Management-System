# -*- coding: utf-8 -*-
"""幂等安装团购活动菜单并建立缺失表：python -m app.scripts.install_group_activity。

- 只创建缺失表、同步菜单与管理员绑定，不重置已有数据
- 仅当活动表为空时写入几条演示数据（引用当前库真实规则 / 订单 / 会员）
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select

from app.api.v1.system.group_activity.model import GroupActivity, GroupActivityMember
from app.api.v1.system.group_rule.model import GroupRule
from app.api.v1.system.member.model import Member
from app.api.v1.system.menu.model import Menu
from app.api.v1.system.order.model import Order
from app.api.v1.system.roles.model import RoleMenu, Roles
from app.database.database import create_tables
from app.database.sqlalchemy import async_session_factory, engine


async def install() -> None:
    """创建缺失表、同步推广管理菜单、绑定管理员，并按需写入演示活动。"""
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

            count = await session.scalar(select(func.count()).select_from(GroupActivity))
            if count:
                print(f"团购活动表已有 {count} 条数据，跳过演示数据")
            else:
                rules = (await session.scalars(select(GroupRule).order_by(GroupRule.id.asc()).limit(2))).all()
                orders = (await session.scalars(select(Order.id).order_by(Order.id.asc()).limit(3))).all()
                members = (await session.scalars(select(Member.id).order_by(Member.id.asc()).limit(3))).all()
                if not rules or not orders or not members:
                    print("缺少团购规则 / 订单 / 会员，跳过演示数据")
                else:
                    plan = [
                        (0, 0, 0, [0, 1], datetime(2022, 5, 9, 16, 30, 39)),
                        (1, 1, 1, [1], datetime(2022, 5, 12, 9, 20, 10)),
                        (0, 2 % len(orders), 2 % len(members), [], datetime(2022, 5, 20, 14, 5, 0)),
                    ]
                    added = 0
                    for rule_index, order_index, member_index, join_indexes, start_time in plan:
                        if rule_index >= len(rules) or order_index >= len(orders) or member_index >= len(members):
                            continue
                        rule = rules[rule_index]
                        order_id = orders[order_index]
                        member_id = members[member_index]
                        activity = GroupActivity(
                            rule_id=rule.id,
                            order_id=order_id,
                            member_id=member_id,
                            participants=len([i for i in join_indexes if i < len(orders) and i < len(members)]),
                            discount=rule.discount,
                            people=rule.people,
                            share_image="",
                            start_time=start_time,
                            end_time=rule.end_time,
                            enabled_flag=True,
                        )
                        session.add(activity)
                        await session.flush()
                        for join_index in join_indexes:
                            if join_index >= len(orders) or join_index >= len(members):
                                continue
                            session.add(
                                GroupActivityMember(
                                    activity_id=activity.id,
                                    order_id=orders[join_index],
                                    member_id=members[join_index],
                                    join_time=start_time,
                                    enabled_flag=True,
                                )
                            )
                        added += 1
                    print(f"写入 {added} 条演示团购活动")

    print("团购活动表和菜单安装完成")


if __name__ == "__main__":
    async def main() -> None:
        try:
            await install()
        finally:
            await engine.dispose()

    asyncio.run(main())
