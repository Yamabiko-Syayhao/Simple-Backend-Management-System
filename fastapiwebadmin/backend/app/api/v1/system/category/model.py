# -*- coding: utf-8 -*-
"""商品类目数据层"""

import typing

from sqlalchemy import BigInteger, Column, Integer, String, Text, and_, func, or_, select

from app.models.base import Base


class Category(Base):
    """商品类目表 mal_category（两级：一级类目 / 二级类目）"""

    __tablename__ = "mal_category"

    name = Column(String(128), nullable=False, comment="类目名称", index=True)
    keywords = Column(String(255), nullable=True, comment="关键字")
    level = Column(Integer, nullable=False, default=1, comment="级别 1一级类目 2二级类目", index=True)
    parent_id = Column(BigInteger, nullable=False, default=0, comment="父类目ID，一级类目为 0", index=True)
    icon = Column(Text, nullable=True, comment="类目图标 URL")
    image = Column(Text, nullable=True, comment="类目图片 URL")
    description = Column(String(500), nullable=True, comment="类目简介")

    @classmethod
    async def get_all(cls) -> typing.List[typing.Dict[str, typing.Any]]:
        """类目数量有限，一次性返回全部（不分页），由前端组装成树"""
        stmt = (
            select(cls.get_table_columns())
            .where(cls.enabled_flag.is_(True))
            .order_by(cls.level.asc(), cls.id.asc())
        )
        return await cls.get_result(stmt) or []

    @classmethod
    async def get_children(cls, parent_id: int) -> typing.List[typing.Dict[str, typing.Any]]:
        stmt = select(cls.get_table_columns()).where(
            cls.parent_id == parent_id, cls.enabled_flag.is_(True)
        )
        return await cls.get_result(stmt) or []

    @classmethod
    def client_scope_ids(cls, category_id: int):
        """客户端商品范围：一级及其二级，二级仅自身；无效类目不匹配。"""
        root_ids = select(cls.id).where(
            cls.enabled_flag.is_(True), cls.level == 1, cls.parent_id == 0
        )
        return select(cls.id).where(
            cls.enabled_flag.is_(True),
            or_(
                and_(
                    cls.id == category_id,
                    or_(
                        and_(cls.level == 1, cls.parent_id == 0),
                        and_(cls.level == 2, cls.parent_id.in_(root_ids)),
                    ),
                ),
                and_(
                    cls.level == 2,
                    cls.parent_id == category_id,
                    cls.parent_id.in_(root_ids),
                ),
            ),
        )

    @classmethod
    async def count_children(cls, parent_id: int) -> int:
        stmt = select(func.count()).select_from(cls).where(
            cls.parent_id == parent_id, cls.enabled_flag.is_(True)
        )
        result = await cls.execute(stmt)
        return result.scalar() or 0
