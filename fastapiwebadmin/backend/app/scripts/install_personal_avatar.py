# -*- coding: utf-8 -*-
"""把 sys_user.avatar 扩成 MEDIUMTEXT（幂等），供头像 base64 存储：

    python -m app.scripts.install_personal_avatar

背景：原列是 TEXT（最大 64KB），裁剪后的 base64 头像可能超过 64KB 导致
`(1406, Data too long for column 'avatar')`，个人中心换头像直接失败。
"""

import asyncio

from sqlalchemy import text

from app.database.database import create_tables
from app.database.sqlalchemy import async_session_factory, engine


async def install() -> None:
    await create_tables()
    async with async_session_factory() as session, session.begin():
        row = (await session.execute(text(
            "SELECT DATA_TYPE FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'sys_user' AND COLUMN_NAME = 'avatar'"
        ))).first()
        if not row:
            raise ValueError("sys_user.avatar 列不存在，请先初始化数据库")
        current = (row[0] or "").lower()
        print(f"当前 sys_user.avatar 类型: {current}")
        if current in ("mediumtext", "longtext"):
            print("已经是 MEDIUMTEXT 及以上，跳过")
            return
        await session.execute(text("ALTER TABLE sys_user MODIFY COLUMN avatar MEDIUMTEXT NOT NULL"))
        print("已改为 MEDIUMTEXT")


if __name__ == "__main__":
    async def main() -> None:
        try:
            await install()
        finally:
            await engine.dispose()

    asyncio.run(main())
