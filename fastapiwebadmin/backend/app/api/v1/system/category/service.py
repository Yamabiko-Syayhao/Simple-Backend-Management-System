# -*- coding: utf-8 -*-
"""商品类目业务层"""

import typing

from sqlalchemy import select

from app.api.v1.system.category.model import Category
from app.api.v1.system.category.schema import CategoryIn


class CategoryService:
    """商品类目管理（两级树）"""

    @staticmethod
    async def list() -> typing.Dict[str, typing.Any]:
        rows = await Category.get_all()
        return {"rows": rows, "total": len(rows)}

    @staticmethod
    async def detail(category_id: int) -> typing.Dict[str, typing.Any]:
        category = await Category.get(category_id, to_dict=True)
        if not category:
            raise ValueError("类目不存在")
        return category

    # ---------------------------------------------------------------- 客户端（只读）
    @staticmethod
    async def client_list() -> typing.List[typing.Dict[str, typing.Any]]:
        """一级类目，供首页快捷入口使用"""
        rows = await Category.get_all()
        result = []
        for row in rows:
            if row.get("level") != 1:
                continue
            result.append(
                {
                    "id": row.get("id"),
                    "name": row.get("name"),
                    "icon": row.get("icon") or "",
                    "image": row.get("image") or "",
                }
            )
        return result[:10]

    @staticmethod
    async def client_tree() -> typing.List[typing.Dict[str, typing.Any]]:
        """复用后台类目数据，仅返回有效两级树及客户端展示字段。"""
        rows = await Category.get_all()
        roots = {}
        fields = ("id", "name", "level", "parent_id", "icon", "image", "description")

        def public_row(row):
            return {
                key: (row.get(key) or "") if key in ("icon", "image", "description") else row.get(key)
                for key in fields
            }

        for row in rows:
            if row.get("level") == 1 and row.get("parent_id") == 0:
                roots[row["id"]] = {**public_row(row), "children": []}
        for row in rows:
            parent = roots.get(row.get("parent_id"))
            if row.get("level") == 2 and parent is not None:
                parent["children"].append(public_row(row))
        result = sorted(roots.values(), key=lambda row: row["id"])
        for row in result:
            row["children"].sort(key=lambda child: child["id"])
        return result

    @staticmethod
    async def save_or_update(params: CategoryIn) -> typing.Dict[str, typing.Any]:
        payload = params.model_dump()

        name = (payload.get("name") or "").strip()
        if not name:
            raise ValueError("类目名称不能为空")
        payload["name"] = name

        level = payload.get("level") or 1
        parent_id = payload.get("parent_id") or 0

        if level == 1:
            parent_id = 0
        else:
            if not parent_id:
                raise ValueError("二级类目必须选择父类目")
            parent = await Category.get(parent_id, to_dict=True)
            if not parent or parent.get("level") != 1:
                raise ValueError("父类目不存在或不是一级类目")

        payload["level"] = level
        payload["parent_id"] = parent_id

        # 父类目不能是自己
        if parent_id and parent_id == payload.get("id"):
            raise ValueError("父类目不能是自己")

        # 已经有子类目的一级类目，不允许改成二级（否则子类目会变成孤儿）
        if payload.get("id") and level == 2:
            children = await Category.count_children(payload["id"])
            if children:
                raise ValueError("该类目下存在子类目，不能改为二级类目")

        # 同一父级下类目名不允许重复
        stmt = select(Category.id).where(
            Category.name == name,
            Category.parent_id == parent_id,
            Category.enabled_flag.is_(True),
        )
        if payload.get("id"):
            stmt = stmt.where(Category.id != payload["id"])
        if await Category.get_result(stmt, first=True):
            raise ValueError("同级下已存在同名类目")

        if not payload.get("id"):
            created = await Category.create(payload, to_dict=True)
            return {"id": created.get("id") if created else None}

        current = await Category.get(payload["id"])
        if not current:
            raise ValueError("类目不存在")
        await Category.update(payload)
        return {"id": payload["id"]}

    @staticmethod
    async def deleted(category_id: int) -> int:
        children = await Category.count_children(category_id)
        if children:
            raise ValueError("该类目下存在子类目，请先删除子类目")
        # 物理删除
        return await Category.delete(category_id, True)
