"""幂等扩展既有订单表的金额/幂等/商品快照字段，不重置数据。"""
import asyncio

from sqlalchemy import inspect, text

from app.database.database import create_tables
from app.database.sqlalchemy import engine


async def install():
    await create_tables()
    additions = {
        "mal_order": {"goods_amount": "DECIMAL(12,2) NULL", "freight_amount": "DECIMAL(12,2) NULL",
                      "discount_amount": "DECIMAL(12,2) NULL", "coupon_user_id": "BIGINT NULL",
                      "checkout_key": "VARCHAR(80) NULL"},
        "mal_order_item": {"goods_id": "BIGINT NULL", "product_id": "BIGINT NULL"},
    }
    async with engine.begin() as conn:
        for table, columns in additions.items():
            existing = await conn.run_sync(lambda sync, table=table: inspect(sync).get_columns(table))
            names = {column["name"] for column in existing}
            for name, declaration in columns.items():
                if name not in names:
                    await conn.execute(text(f"ALTER TABLE `{table}` ADD COLUMN `{name}` {declaration}"))
            if table == "mal_order_item":
                spec = next(column for column in existing if column["name"] == "spec")
                if (getattr(spec["type"], "length", 128) or 128) < 128:
                    await conn.execute(text("ALTER TABLE `mal_order_item` MODIFY COLUMN `spec` VARCHAR(128) NULL"))
        indexes = await conn.run_sync(lambda sync: inspect(sync).get_indexes("mal_order"))
        if not any(row["name"] == "uq_order_member_checkout" for row in indexes):
            await conn.execute(text("CREATE UNIQUE INDEX uq_order_member_checkout ON mal_order(member_id, checkout_key)"))
    print("订单字段与幂等索引检查完成，原订单保留")


if __name__ == "__main__":
    async def main():
        try:
            await install()
        finally:
            await engine.dispose()
    asyncio.run(main())
