# -*- coding: utf-8 -*-
"""会员购物车数据层；商品信息实时关联已有商品和库存表。"""

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, UniqueConstraint, select

from app.api.v1.system.goods.model import Goods, GoodsProduct
from app.models.base import Base


class Cart(Base):
    """一位会员的同一库存规格只有一条购物车记录。"""

    __tablename__ = "mal_cart"
    __table_args__ = (UniqueConstraint("member_id", "product_id", name="uq_cart_member_product"),)

    member_id = Column(BigInteger, ForeignKey("mal_member.id", ondelete="CASCADE"), nullable=False, index=True)
    # 保留失效条目，允许会员清理后台已删除的商品或规格。
    goods_id = Column(BigInteger, ForeignKey("mal_goods.id", ondelete="SET NULL"), nullable=True, index=True)
    product_id = Column(BigInteger, ForeignKey("mal_goods_product.id", ondelete="SET NULL"), nullable=True, index=True)
    quantity = Column(Integer, nullable=False, default=1, comment="加入数量，不预占库存")
    checked = Column(Boolean, nullable=False, default=True, comment="是否勾选")

    @classmethod
    def _build_stmt(cls, member_id: int):
        return (
            select(cls, Goods, GoodsProduct)
            .select_from(cls)
            .outerjoin(Goods, Goods.id == cls.goods_id)
            .outerjoin(GoodsProduct, GoodsProduct.id == cls.product_id)
            .where(cls.member_id == member_id, cls.enabled_flag.is_(True))
            .order_by(cls.creation_date.desc(), cls.id.desc())
        )

    @classmethod
    async def get_list(cls, member_id: int, session):
        return (await session.execute(cls._build_stmt(member_id))).all()
