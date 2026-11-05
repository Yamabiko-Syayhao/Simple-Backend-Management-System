"""rename system tables to sys_ prefix

Revision ID: a8f3c2e91b04
Revises: d45d346a66e1
Create Date: 2026-09-28 15:16:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "a8f3c2e91b04"
down_revision = "d45d346a66e1"
branch_labels = None
depends_on = None

TABLE_RENAMES = [
    ("user", "sys_user"),
    ("user_roles", "sys_user_role"),
    ("roles", "sys_role"),
    ("role_menus", "sys_role_menu"),
    ("role_depts", "sys_role_dept"),
    ("menu", "sys_menu"),
    ("menu_view_history", "sys_menu_view_history"),
    ("department", "sys_dept"),
    ("lookup", "sys_dict_type"),
    ("lookup_value", "sys_dict_data"),
    ("operation_log", "sys_operation_log"),
    ("user_login_record", "sys_login_record"),
    ("file_info", "sys_file"),
]


def _rename_tables(pairs: list[tuple[str, str]]) -> None:
    bind = op.get_bind()
    inspector = __import__("sqlalchemy").inspect(bind)
    existing = set(inspector.get_table_names())
    for old_name, new_name in pairs:
        if old_name in existing and new_name not in existing:
            op.rename_table(old_name, new_name)


def upgrade() -> None:
    _rename_tables(TABLE_RENAMES)


def downgrade() -> None:
    _rename_tables([(new_name, old_name) for old_name, new_name in TABLE_RENAMES])
