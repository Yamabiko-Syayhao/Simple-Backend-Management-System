"""将模型的结构化工具参数转换为授权范围内的只读查询。"""

import asyncio
import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import JSON, Boolean, Date, DateTime, Float, Integer, Numeric, String, cast, func, inspect, select
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.system.ai_assistant.data_catalog import SOLAR_SCHEDULE, SUPER_ADMIN_ONLY, TABLES
from app.api.v1.system.coupon.model import Coupon, CouponUser
from app.api.v1.system.roles.model import Roles
from app.api.v1.system.user.model import User
from app.core.data_scope import DataScopeFilter
from app.core.permission import PermissionService
from app.database.sqlalchemy import async_session_factory
from app.models.base import DeclarativeRoot
from app.utils.import_util import ImportUtil

MAX_ROWS = 20
MAX_TEXT_LENGTH = 240
MAX_RESULT_BYTES = 8192
DEFAULT_COLUMNS = 8


class TableInput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    table: str = Field(description="list_tables 返回的表名")


class FilterInput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    column: str = Field(description="describe_table 返回的字段名")
    op: Literal["eq", "ne", "gt", "gte", "lt", "lte", "contains"] = Field(
        description="eq/ne 等于/不等于，gt/gte/lt/lte 比较，contains 按字面包含（文本）",
    )
    value: str | int | float | bool | None = Field(
        description="按字段类型提供值，日期时间用 ISO 格式，eq/ne 可用 null",
    )


class QueryInput(TableInput):
    mode: Literal["rows", "count", "group_count"] = Field(
        description="rows 分页明细；count 精确总数；group_count 按字段分组精确计数",
    )
    filters: list[FilterInput] = Field(default_factory=list, max_length=8, description="筛选条件，同时满足")
    columns: list[str] = Field(default_factory=list, max_length=12, description="rows 指定返回字段")
    group_by: str | None = Field(default=None, description="group_count 的分组字段，例如 status")
    order_by: str | None = Field(default=None, description="rows 排序字段，默认按主键降序")
    order: Literal["asc", "desc"] = "desc"
    limit: int = Field(default=8, ge=1, le=MAX_ROWS, description="分页最多返回的记录数")
    offset: int = Field(default=0, ge=0, le=1_000_000, description="后续页使用上一次返回的 next_offset")


def _function_tool(name: str, description: str, schema: dict) -> dict:
    return {
        "type": "function",
        "function": {"name": name, "description": description, "parameters": schema},
    }


TOOLS = [
    _function_tool("list_tables", "列出当前用户可查询的商城和后台业务表", {
        "type": "object", "properties": {}, "additionalProperties": False,
    }),
    _function_tool("describe_table", "查看一张表的字段、字段含义和关联，状态码以字段说明为准",
                   TableInput.model_json_schema()),
    _function_tool("query_table", "读取一张授权表的明细、精确计数或按字段分组的计数。"
                   "跨表问题根据 describe_table 提示的 ID 逐表查询。", QueryInput.model_json_schema()),
]


@lru_cache(maxsize=1)
def _registered_tables():
    ImportUtil.find_models(DeclarativeRoot)
    return DeclarativeRoot.metadata.tables


async def _optional_solar_table():
    # Beat 可以使用独立的库，只在当前应用库确实有这张表时开放。
    async def table_exists():
        async with async_session_factory() as session:
            connection = await session.connection()
            return await connection.run_sync(lambda conn: inspect(conn).has_table(SOLAR_SCHEDULE))

    try:
        exists = await asyncio.wait_for(table_exists(), timeout=2)
    except (SQLAlchemyError, asyncio.TimeoutError):
        return None
    if exists:
        from app.plugin.fea_celery.scheduler.models import SolarSchedule

        return SolarSchedule.__table__
    return None


def _column_value(column, value):
    """校验并转换比较值，避免数据库隐式转换或跨方言比较差异。"""
    if value is None:
        return None
    column_type = column.type
    try:
        if isinstance(column_type, Boolean) and isinstance(value, bool):
            return value
        if isinstance(column_type, Integer) and type(value) is int and -(2**63) <= value < 2**63:
            return value
        if isinstance(column_type, (Numeric, Float)) and type(value) in (int, float):
            number = Decimal(str(value))
            if number.is_finite():
                return number
        if isinstance(value, str) and len(value) <= 240 and "\x00" not in value:
            if isinstance(column_type, DateTime):
                parsed = datetime.fromisoformat(value)
                if parsed.tzinfo is None:
                    return parsed
            elif isinstance(column_type, Date):
                return date.fromisoformat(value)
            elif isinstance(column_type, String):
                return value
    except (ValueError, InvalidOperation):
        pass
    raise ValueError("筛选值与字段类型不匹配。日期时间使用无时区的 ISO 格式。")


def _condition(column, condition: FilterInput):
    value = _column_value(column, condition.value)
    if condition.op == "eq":
        return column == value
    if condition.op == "ne":
        return column != value
    if value is None:
        raise ValueError("只有 eq 或 ne 可以比较 null。")
    if condition.op == "contains":
        if not isinstance(column.type, String):
            raise ValueError("contains 只能用于文本字段。")
        return column.contains(value, autoescape=True)
    if condition.op == "gt":
        return column > value
    if condition.op == "gte":
        return column >= value
    if condition.op == "lt":
        return column < value
    return column <= value


def _safe_value(value, json_column: bool):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, str):
        if len(value) > MAX_TEXT_LENGTH:
            return value[:MAX_TEXT_LENGTH] + "…"
        if json_column:
            try:
                return json.loads(value)
            except ValueError:
                pass
    return value


def _bounded_page(rows, query: QueryInput, json_columns: set[str]) -> dict:
    result = {"rows": [], "next_offset": None}
    for row in rows[:query.limit]:
        result["rows"].append({key: _safe_value(value, key in json_columns) for key, value in row.items()})
        if len(json.dumps(result["rows"], ensure_ascii=False).encode("utf-8")) > MAX_RESULT_BYTES - 128:
            result["rows"].pop()
            break
    if len(rows) > len(result["rows"]):
        if not result["rows"]:
            raise ValueError("单行结果过大，请减少返回字段。")
        result["next_offset"] = query.offset + len(result["rows"])
    return result


class AssistantDataTools:
    tools = TOOLS

    def __init__(self, access: dict, scope: DataScopeFilter, tables) -> None:
        self.access = access
        self.scope = scope
        self.tables = tables

    @classmethod
    async def for_user(cls, user: User) -> "AssistantDataTools":
        super_admin = PermissionService.is_super_admin(user.user_type)
        permissions = set() if super_admin else set(await PermissionService.get_permission_codes(user))
        registered = dict(_registered_tables())
        if super_admin:
            solar = await _optional_solar_table()
            if solar is not None:
                registered[SOLAR_SCHEDULE] = solar
        access = {
            name: config for name, config in TABLES.items()
            if name in registered and (
                super_admin or not config.permission
                or (config.permission != SUPER_ADMIN_ONLY and config.permission in permissions)
            )
        }
        return cls(access, await DataScopeFilter.for_user(user), registered)

    def _table(self, name: str):
        if name not in self.access:
            raise ValueError("表不存在或当前用户没有查询权限。")
        table = self.tables[name]
        source = table
        available = dict(table.c.items())
        comments = {column.name: column.comment or "" for column in table.c}
        if name in {"mal_coupon", "mal_coupon_user"}:
            if name == "mal_coupon_user":
                source = table.outerjoin(Coupon.__table__, table.c.coupon_id == Coupon.id)
                expression = CouponUser._status_expression()
            else:
                expression = Coupon._status_expression()
            available["effective_status"] = expression
            comments["effective_status"] = "按当前时间及后台业务规则计算的状态，状态码同 status"
        if name == "mal_order" and "mal_member" in self.access:
            member = self.tables["mal_member"]
            source = table.outerjoin(member, (member.c.id == table.c.member_id) & member.c.enabled_flag.is_(True))
            available["member_account"] = member.c.username
            comments["member_account"] = "下单会员的当前登录账号"
        names = [column.name for column in table.primary_key.columns]
        names.extend(self.access[name].fields.split())
        if "member_account" in available:
            names.insert(4, "member_account")
        if "creation_date" in available:
            names.extend(("creation_date", "updation_date"))
        return table, source, {key: available[key] for key in names}, comments

    def _row_scope(self, table):
        if table.name == "sys_user":
            return self.scope.user_clause(User)
        if table.name == "sys_dept":
            visible_ids = self.scope.dept_visible_ids()
            return None if visible_ids is None else table.c.id.in_(visible_ids)
        if table.name == "sys_role":
            return self.scope.role_clause(Roles)
        if table.name in {"sys_role_dept", "sys_role_menu"}:
            role_scope = self.scope.role_clause(Roles)
            role_ids = select(Roles.id).where(Roles.enabled_flag.is_(True))
            if role_scope is not None:
                role_ids = role_ids.where(role_scope)
            return table.c.role_id.in_(role_ids)
        if table.name == "sys_user_role":
            user_ids = select(User.id).where(User.enabled_flag.is_(True))
            user_scope = self.scope.user_clause(User)
            if user_scope is not None:
                user_ids = user_ids.where(user_scope)
            return table.c.user_id.in_(user_ids)
        if table.name in {"sys_login_record", "sys_operation_log"}:
            return self.scope.log_user_clause(table.c.user_id)
        return None

    async def execute(self, name: str, arguments: dict) -> dict:
        try:
            if name == "list_tables" and arguments == {}:
                return {"tables": [{"table": key, "name": value.title} for key, value in self.access.items()]}
            if name == "describe_table":
                query = TableInput.model_validate(arguments)
                _, _, columns, comments = self._table(query.table)
                return {
                    "table": query.table,
                    "columns": {key: {"type": str(column.type), "description": comments[key]}
                                for key, column in columns.items()},
                    "relations": self.access[query.table].relations,
                    "scope": "查询仅包含当前用户可见且未删除的记录",
                }
            if name == "query_table":
                return await self._query(QueryInput.model_validate(arguments))
        except ValidationError:
            raise ValueError("工具参数无效，请按工具定义提交。") from None
        raise ValueError("未提供有效的查询工具。")

    async def _query(self, query: QueryInput) -> dict:
        table, source, columns, _ = self._table(query.table)

        def get_column(key: str):
            if key not in columns:
                raise ValueError("字段不存在或当前用户没有读取权限。")
            return columns[key]

        filters = [_condition(get_column(item.column), item) for item in query.filters]
        if "enabled_flag" in table.c:
            filters.append(table.c.enabled_flag.is_(True))
        scope = self._row_scope(table)
        if scope is not None:
            filters.append(scope)

        count = func.count().label("count")
        json_columns = set()
        if query.mode == "count":
            statement = select(count).select_from(source).where(*filters)
        elif query.mode == "group_count":
            group = get_column(query.group_by or "")
            if isinstance(group.type, JSON) or (
                isinstance(group.type, String) and (group.type.length or MAX_TEXT_LENGTH + 1) > MAX_TEXT_LENGTH
            ):
                raise ValueError("长文本字段无法分组，请使用状态、编号或其他短字段。")
            statement = (select(group.label(query.group_by), count).select_from(source)
                         .where(*filters).group_by(group).order_by(count.desc(), group.asc()))
        else:
            projection = []
            for key in dict.fromkeys(query.columns or list(columns)[:DEFAULT_COLUMNS]):
                column = get_column(key)
                if isinstance(column.type, JSON):
                    json_columns.add(key)
                    column = cast(column, String)
                if isinstance(column.type, String):
                    column = func.substr(column, 1, MAX_TEXT_LENGTH + 1)
                projection.append(column.label(key))
            order = [column.desc() for column in table.primary_key.columns]
            if query.order_by:
                column = get_column(query.order_by)
                if isinstance(column.type, JSON):
                    raise ValueError("JSON 字段不支持排序。")
                order.insert(0, column.asc() if query.order == "asc" else column.desc())
            statement = select(*projection).select_from(source).where(*filters).order_by(*order)

        if query.mode != "count":
            statement = statement.offset(query.offset).limit(query.limit + 1)
        try:
            async with async_session_factory() as session:
                result = await asyncio.wait_for(session.execute(statement), timeout=8)
                if query.mode == "count":
                    return {"count": result.scalar_one()}
                return _bounded_page(result.mappings().all(), query, json_columns)
        except asyncio.TimeoutError:
            raise ValueError("查询超时，请缩小筛选范围。") from None
        except SQLAlchemyError:
            raise ValueError("数据暂时无法读取。") from None
