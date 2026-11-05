# -*- coding: utf-8 -*-
"""数据库初始化与种子数据导入"""

import json
from typing import Any

from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.department.model import Department
from app.api.v1.system.menu.model import Menu
from app.api.v1.system.roles.model import RoleMenu, Roles
from app.api.v1.system.user.model import User, UserRole
from app.config.path_conf import SCRIPT_DIR
from app.config.setting import settings
from app.core.logger import log
from app.database.database import create_tables
from app.database.sqlalchemy import async_session_factory


class InitializeData:
    """启动时建表并按表导入 scripts/data 下的初始化 JSON。"""

    def __init__(self) -> None:
        self.prepare_init_models = [
            Department,
            Menu,
            Roles,
            User,
            UserRole,
            RoleMenu,
        ]

    async def init_db(self) -> None:
        if not settings.SQL_DB_ENABLE:
            log.warning("SQL_DB_ENABLE=False，跳过数据库初始化")
            return

        if settings.AUTO_CREATE_TABLES:
            await create_tables()

        if settings.AUTO_SEED_DATA:
            async with async_session_factory() as session:
                async with session.begin():
                    await self._init_data(session)
            log.info("默认账号: admin / 123456")

        if settings.AUTO_CREATE_TABLES:
            await self._patch_schema()

    async def _init_data(self, session: AsyncSession) -> None:
        for model in self.prepare_init_models:
            table_name = model.__tablename__
            count = await session.scalar(select(func.count()).select_from(model))
            if count and count > 0:
                log.info(f"跳过 {table_name} 初始化（已有 {count} 条记录）")
                continue

            data = self._load_json(table_name)
            if not data and table_name != "sys_role_menu":
                log.info(f"跳过 {table_name}，无初始化数据文件")
                continue

            try:
                if table_name == "sys_menu":
                    await self._insert_menu_tree(session, data)
                elif table_name == "sys_role_menu":
                    await self._bind_admin_role_menus(session)
                else:
                    session.add_all([model(**item) for item in data])
                await session.flush()
                log.info(f"已写入 {table_name} 初始化数据")
            except Exception as exc:
                log.error(f"初始化 {table_name} 失败: {exc}")
                raise

    @staticmethod
    def _load_json(table_name: str) -> list[dict[str, Any]]:
        json_path = SCRIPT_DIR / f"{table_name}.json"
        if not json_path.exists():
            return []
        with open(json_path, encoding="utf-8") as file:
            return json.loads(file.read())

    @staticmethod
    async def _insert_menu_tree(
        session: AsyncSession,
        items: list[dict[str, Any]],
        parent_id: int = 0,
    ) -> None:
        """将嵌套 children 菜单树写入数据库（通过 parent_id 关联）。"""
        for item in items:
            row = dict(item)
            children = row.pop("children", [])
            row.setdefault("parent_id", parent_id)
            row.setdefault("isLink", 0)
            row.setdefault("isHide", 0)
            row.setdefault("isKeepAlive", 1)
            row.setdefault("isAffix", 0)
            row.setdefault("isIframe", 0)
            menu = Menu(**row)
            session.add(menu)
            await session.flush()
            if children:
                await InitializeData._insert_menu_tree(session, children, menu.id)

    @staticmethod
    async def _bind_admin_role_menus(session: AsyncSession) -> None:
        """管理员角色绑定全部菜单（sys_role_menu 无独立 JSON 时自动生成）。"""
        role = await session.scalar(
            select(Roles.id).where(Roles.name == "管理员", Roles.enabled_flag.is_(True))
        )
        if not role:
            log.warning("未找到管理员角色，跳过 sys_role_menu 初始化")
            return
        menu_ids = (await session.scalars(select(Menu.id).where(Menu.enabled_flag.is_(True)))).all()
        if not menu_ids:
            return
        await session.execute(
            insert(RoleMenu),
            [{"role_id": role, "menu_id": menu_id} for menu_id in menu_ids],
        )

    async def _patch_schema(self) -> None:
        """为已有 MySQL 库补充新增字段/表（非破坏性，仅 MySQL 遗留升级路径）。"""
        if not settings.SQL_DB_ENABLE or settings.DATABASE_TYPE != "mysql":
            return

        import pymysql

        alters = [
            "ALTER TABLE `sys_file` ADD COLUMN `storage_type` varchar(32) NULL DEFAULT 'local' COMMENT '存储类型'",
            "ALTER TABLE `sys_file` ADD COLUMN `file_url` varchar(1000) NULL COMMENT '访问URL'",
            "ALTER TABLE `sys_file` ADD COLUMN `file_hash` varchar(64) NULL COMMENT '文件MD5'",
            "ALTER TABLE `sys_file` ADD COLUMN `uploader_id` int NULL COMMENT '上传者ID'",
            "ALTER TABLE `sys_file` ADD COLUMN `uploader_name` varchar(64) NULL COMMENT '上传者'",
            "ALTER TABLE `sys_role` ADD COLUMN `data_scope` int NOT NULL DEFAULT 4 COMMENT '数据权限范围(1:仅本人 2:本部门 3:本部门及以下 4:全部 5:自定义)'",
        ]
        create_tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS `sys_role_dept` (
              `role_id` int NOT NULL COMMENT '角色ID',
              `dept_id` int NOT NULL COMMENT '部门ID',
              PRIMARY KEY (`role_id`, `dept_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色自定义数据权限部门'
            """,
            """
            CREATE TABLE IF NOT EXISTS `sys_user_role` (
              `user_id` bigint NOT NULL COMMENT '用户ID',
              `role_id` int NOT NULL COMMENT '角色ID',
              PRIMARY KEY (`user_id`, `role_id`),
              KEY `idx_sys_user_role_role_id` (`role_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表'
            """,
            """
            CREATE TABLE IF NOT EXISTS `sys_role_menu` (
              `role_id` int NOT NULL COMMENT '角色ID',
              `menu_id` int NOT NULL COMMENT '菜单ID',
              PRIMARY KEY (`role_id`, `menu_id`),
              KEY `idx_sys_role_menu_menu_id` (`menu_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色菜单关联表'
            """,
        ]
        try:
            conn = pymysql.connect(
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                database=settings.DATABASE_NAME,
                charset="utf8mb4",
            )
            cursor = conn.cursor()
            for sql in alters:
                try:
                    cursor.execute(sql)
                except Exception:
                    pass
            for sql in create_tables_sql:
                try:
                    cursor.execute(sql)
                except Exception:
                    pass
            self._migrate_rbac_data(cursor)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as exc:
            log.warning(f"schema patch 跳过: {exc}")

    @staticmethod
    def _migrate_rbac_data(cursor) -> None:
        """将历史 JSON/CSV 权限数据迁移到规范关联表（仅 MySQL 遗留库）。"""
        try:
            user_role_table = InitializeData._resolve_table_name(cursor, "sys_user_role", "user_roles")
            cursor.execute(f"SELECT COUNT(*) AS cnt FROM `{user_role_table}`")
            user_role_count = cursor.fetchone()[0]
            user_table = InitializeData._resolve_table_name(cursor, "sys_user", "user")
            if user_role_count == 0 and InitializeData._column_exists(cursor, user_table, "roles"):
                cursor.execute(
                    f"SELECT id, roles FROM `{user_table}` WHERE enabled_flag = 1 AND roles IS NOT NULL"
                )
                migrated = UserRole.migrate_from_legacy_json(cursor, cursor.fetchall())
                if migrated:
                    log.info(f"RBAC 迁移: {user_role_table} 写入 {migrated} 条")

            role_menu_table = InitializeData._resolve_table_name(cursor, "sys_role_menu", "role_menus")
            cursor.execute(f"SELECT COUNT(*) AS cnt FROM `{role_menu_table}`")
            role_menu_count = cursor.fetchone()[0]
            role_table = InitializeData._resolve_table_name(cursor, "sys_role", "roles")
            if role_menu_count == 0 and InitializeData._column_exists(cursor, role_table, "menus"):
                cursor.execute(
                    f"SELECT id, menus FROM `{role_table}` WHERE enabled_flag = 1 AND menus IS NOT NULL AND menus <> ''"
                )
                migrated = RoleMenu.migrate_from_legacy_csv(cursor, cursor.fetchall())
                if migrated:
                    log.info(f"RBAC 迁移: {role_menu_table} 写入 {migrated} 条")

            InitializeData._drop_legacy_rbac_columns(cursor)
        except Exception as exc:
            log.warning(f"RBAC 数据迁移跳过: {exc}")

    @staticmethod
    def _table_exists(cursor, table: str) -> bool:
        cursor.execute("SHOW TABLES LIKE %s", (table,))
        return cursor.fetchone() is not None

    @staticmethod
    def _resolve_table_name(cursor, new_name: str, old_name: str) -> str:
        if InitializeData._table_exists(cursor, new_name):
            return new_name
        return old_name

    @staticmethod
    def _column_exists(cursor, table: str, column: str) -> bool:
        cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE %s", (column,))
        return cursor.fetchone() is not None

    @staticmethod
    def _drop_legacy_rbac_columns(cursor) -> None:
        drops = []
        user_role_table = InitializeData._resolve_table_name(cursor, "sys_user_role", "user_roles")
        user_table = InitializeData._resolve_table_name(cursor, "sys_user", "user")
        role_menu_table = InitializeData._resolve_table_name(cursor, "sys_role_menu", "role_menus")
        role_table = InitializeData._resolve_table_name(cursor, "sys_role", "roles")
        cursor.execute(f"SELECT COUNT(*) FROM `{user_role_table}`")
        if cursor.fetchone()[0] > 0 and InitializeData._column_exists(cursor, user_table, "roles"):
            drops.append(f"ALTER TABLE `{user_table}` DROP COLUMN `roles`")
        cursor.execute(f"SELECT COUNT(*) FROM `{role_menu_table}`")
        if cursor.fetchone()[0] > 0 and InitializeData._column_exists(cursor, role_table, "menus"):
            drops.append(f"ALTER TABLE `{role_table}` DROP COLUMN `menus`")
        for sql in drops:
            try:
                cursor.execute(sql)
                log.info(f"RBAC 清理: {sql}")
            except Exception as exc:
                log.warning(f"RBAC 清理跳过: {exc}")

    @staticmethod
    async def reset_db() -> None:
        """删表重建并导入种子（CLI reset 使用）。"""
        from app.database.database import drop_tables

        await drop_tables()
        initializer = InitializeData()
        await initializer.init_db()
