"""建立缺失购物车表，不改动商品/会员数据：python -m app.scripts.install_cart。"""

import asyncio

from app.database.database import create_tables
from app.database.sqlalchemy import engine


async def install():
    await create_tables()
    print("购物车表检查/创建完成；购物车初始为空，不写入演示购物车")


if __name__ == "__main__":
    async def main():
        try:
            await install()
        finally:
            await engine.dispose()

    asyncio.run(main())
