# -*- coding: utf-8 -*-
"""优惠券与商品使用范围数据层"""

import typing
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, and_, case, or_, select

from app.models.base import Base


class Coupon(Base):
    """优惠券定义表 mal_coupon"""

    __tablename__ = "mal_coupon"

    name = Column(String(128), nullable=False, comment="优惠券名称", index=True)
    description = Column(String(500), nullable=True, comment="介绍")
    tag = Column(String(128), nullable=True, comment="标签")
    min = Column(Numeric(12, 2), nullable=False, default=0, comment="最低消费")
    discount = Column(Numeric(12, 2), nullable=False, default=0, comment="满减金额")
    limit = Column(Integer, nullable=False, default=1, comment="每人限领张数")
    type = Column(Integer, nullable=False, default=0, comment="分发：0通用领券/1注册赠券/2兑换码")
    total = Column(Integer, nullable=False, default=0, comment="优惠券数量，0不限")
    time_type = Column(Integer, nullable=False, default=0, comment="有效期：0相对天数/1绝对时间")
    days = Column(Integer, nullable=False, default=0, comment="领取后有效天数，0领取当日")
    start_time = Column(DateTime, nullable=True, comment="绝对有效期开始时间")
    end_time = Column(DateTime, nullable=True, comment="绝对有效期结束时间")
    goods_type = Column(Integer, nullable=False, default=0, comment="使用范围：0全场/1分类/2商品")
    status = Column(Integer, nullable=False, default=0, comment="状态：0正常/1已过期/2已下架")

    @classmethod
    def _status_expression(cls):
        return case(
            (and_(cls.status == 0, cls.time_type == 1, cls.end_time < datetime.now()), 1),
            else_=cls.status,
        )

    @classmethod
    def _build_stmt(cls, params):
        q = [cls.enabled_flag.is_(True)]
        if getattr(params, "name", None):
            q.append(cls.name.like("%{}%".format(params.name)))
        if getattr(params, "type", None) is not None:
            q.append(cls.type == params.type)
        if getattr(params, "status", None) is not None:
            q.append(cls._status_expression() == params.status)
        return (
            select(cls.get_table_columns()).add_columns(cls._status_expression().label("effective_status"))
            .where(*q)
            .order_by(cls.id.asc() if getattr(params, "sort_order", None) == "asc" else cls.id.desc())
        )

    @classmethod
    async def get_list(cls, params) -> typing.Dict[str, typing.Any]:
        return await cls.pagination(cls._build_stmt(params))

    @classmethod
    async def get_all_by_query(cls, params) -> typing.List[typing.Dict[str, typing.Any]]:
        return await cls.get_result(cls._build_stmt(params)) or []

    @classmethod
    def client_stmt(cls, limit: int = 10):
        """首页普通领券，仅展示已开始且状态正常的通用领券。"""
        return (
            select(cls.get_table_columns())
            .where(
                cls.enabled_flag.is_(True), cls._status_expression() == 0, cls.type == 0,
                or_(cls.time_type == 0, and_(cls.start_time <= datetime.now(), cls.end_time >= datetime.now())),
            )
            .order_by(cls.id.desc())
            .limit(limit)
        )


class CouponCategory(Base):
    """优惠券允许的分类，一张券可关联多个分类"""

    __tablename__ = "mal_coupon_category"
    __table_args__ = (UniqueConstraint("coupon_id", "category_id", name="uq_coupon_category"),)

    coupon_id = Column(BigInteger, ForeignKey("mal_coupon.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(BigInteger, nullable=False, comment="商品类目ID", index=True)


class CouponGoods(Base):
    """优惠券允许的商品，一张券可关联多个商品"""

    __tablename__ = "mal_coupon_goods"
    __table_args__ = (UniqueConstraint("coupon_id", "goods_id", name="uq_coupon_goods"),)

    coupon_id = Column(BigInteger, ForeignKey("mal_coupon.id", ondelete="CASCADE"), nullable=False, index=True)
    goods_id = Column(BigInteger, nullable=False, comment="商品ID", index=True)


class CouponUser(Base):
    """会员领取的优惠券，后续由客户端领券与订单核销流程写入"""

    __tablename__ = "mal_coupon_user"

    coupon_id = Column(BigInteger, ForeignKey("mal_coupon.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, comment="商城会员ID（mal_member.id）", index=True)
    receive_time = Column(DateTime, nullable=False, default=datetime.now, comment="领取时间")
    status = Column(Integer, nullable=False, default=0, comment="使用状态：0未使用/1已使用/2已过期")
    order_id = Column(BigInteger, nullable=True, comment="使用优惠券的订单ID")
    use_time = Column(DateTime, nullable=True, comment="使用时间")
    start_time = Column(DateTime, nullable=True, comment="领券时的有效开始时间快照")
    end_time = Column(DateTime, nullable=True, comment="领券时的有效结束时间快照")

    @classmethod
    def _status_expression(cls):
        """0 未使用 / 1 已使用 / 2 已过期。

        与客户端展示保持同一套口径：
        - 已使用优先；
        - 券被删除、下架、手动置为过期 → 已过期；
        - 绝对有效期券（time_type=1）以**券定义当前时间**为准，后台改期立即生效；
        - 相对天数券（time_type=0）使用持券行的领取快照。
        """
        now = datetime.now()
        expired_by_definition = or_(
            Coupon.enabled_flag.is_(False),
            Coupon.status != 0,
            and_(Coupon.time_type == 1, Coupon.end_time < now),
        )
        expired_by_snapshot = and_(Coupon.time_type == 0, cls.end_time < now)
        return case(
            (cls.status == 1, 1),
            (cls.status == 2, 2),
            (or_(expired_by_definition, expired_by_snapshot), 2),
            else_=0,
        )

    @classmethod
    def _build_stmt(cls, params):
        q = [cls.enabled_flag.is_(True), cls.coupon_id == params.coupon_id]
        if getattr(params, "user_id", None) is not None:
            q.append(cls.user_id == params.user_id)
        if getattr(params, "status", None) is not None:
            q.append(cls._status_expression() == params.status)
        return (
            select(cls.get_table_columns()).add_columns(cls._status_expression().label("effective_status"))
            .select_from(cls)
            .outerjoin(Coupon, Coupon.id == cls.coupon_id)
            .where(*q)
            .order_by(cls.id.asc() if getattr(params, "sort_order", None) == "asc" else cls.id.desc())
        )

    @classmethod
    async def get_list(cls, params) -> typing.Dict[str, typing.Any]:
        return await cls.pagination(cls._build_stmt(params))
