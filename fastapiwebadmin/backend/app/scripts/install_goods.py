"""幂等安装商品菜单并建立缺失表：python -m app.scripts.install_goods。"""
import asyncio
import json
from pathlib import Path
from sqlalchemy import select
from app.database.database import create_tables
from app.database.sqlalchemy import async_session_factory, engine
from app.api.v1.system.menu.model import Menu
from app.api.v1.system.roles.model import Roles, RoleMenu

async def install():
    await create_tables()
    data = json.loads((Path(__file__).parent / 'data/sys_menu.json').read_text(encoding='utf-8'))
    root = next(item for item in data if item['path'] == '/goods')
    async with async_session_factory() as session, session.begin():
        ids = []
        async def upsert(item, parent_id=0):
            values = {k:v for k,v in item.items() if k != 'children'}
            condition = Menu.roles == values['roles'] if values.get('roles') else Menu.path == values['path']
            row = await session.scalar(select(Menu).where(condition))
            if row is None:
                row = Menu(**values, parent_id=parent_id)
                session.add(row)
            else:
                for key,value in values.items(): setattr(row,key,value)
                row.parent_id = parent_id
            await session.flush()
            ids.append(row.id)
            for child in item.get('children',[]): await upsert(child,row.id)
        await upsert(root)
        role_id = await session.scalar(select(Roles.id).where(Roles.name == '管理员'))
        if role_id:
            for menu_id in ids:
                if not await session.get(RoleMenu,(role_id,menu_id)):
                    session.add(RoleMenu(role_id=role_id,menu_id=menu_id))
    print('商品四张表和菜单安装完成')

if __name__ == '__main__':
    async def main():
        try: await install()
        finally: await engine.dispose()
    asyncio.run(main())
