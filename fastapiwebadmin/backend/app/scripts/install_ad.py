# -*- coding: utf-8 -*-
"""幂等安装广告管理菜单并建立缺失表：python -m app.scripts.install_ad。"""

import asyncio
import json
from pathlib import Path

from sqlalchemy import select

from app.api.v1.system.menu.model import Menu
from app.api.v1.system.roles.model import RoleMenu, Roles
from app.database.database import create_tables
from app.database.sqlalchemy import async_session_factory, engine


async def install() -> None:
    """创建缺失表、同步推广管理菜单，并为管理员绑定对应权限。"""
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
    print("广告管理表和菜单安装完成")


if __name__ == "__main__":
    async def main() -> None:
        try:
            await install()
        finally:
            await engine.dispose()

    asyncio.run(main())
