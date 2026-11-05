# -*- coding: utf-8 -*-
"""行政区域业务层"""

import typing

from app.api.v1.system.region.model import Region

LEVEL_TEXT = {1: "省", 2: "市", 3: "区"}


class RegionService:
    """行政区域查询（供后台与客户端共用的基础数据）"""

    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        row["level_name"] = LEVEL_TEXT.get(row.get("level"), "")
        return row

    @staticmethod
    async def tree() -> typing.List[typing.Dict[str, typing.Any]]:
        """返回完整的省 → 市 → 区三级树"""
        rows = await Region.get_all()

        nodes: typing.Dict[int, typing.Dict[str, typing.Any]] = {}
        for row in rows:
            RegionService._decorate(row)
            node = dict(row)
            node["children"] = []
            nodes[node["id"]] = node

        roots: typing.List[typing.Dict[str, typing.Any]] = []
        for row in rows:
            node = nodes[row["id"]]
            parent = nodes.get(node.get("parent_id"))
            if parent is not None:
                parent["children"].append(node)
            else:
                roots.append(node)

        def clean(node: typing.Dict[str, typing.Any]) -> None:
            if not node["children"]:
                node.pop("children", None)
                return
            for child in node["children"]:
                clean(child)

        for root in roots:
            clean(root)
        return roots

    @staticmethod
    async def children(parent_id: int) -> typing.List[typing.Dict[str, typing.Any]]:
        """查询某个区域的直接下级（客户端做省市级联时用）"""
        rows = await Region.get_children(parent_id)
        for row in rows:
            RegionService._decorate(row)
        return rows
