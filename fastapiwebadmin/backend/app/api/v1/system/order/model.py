# -*- coding: utf-8 -*-
"""商城订单数据层"""

import typing

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    delete,
    select,
)

from app.models.base import Base


class Order(Base):
    """商城订单表 mal_order"""

    __tablename__ = "mal_order"
    __table_args__ = (UniqueConstraint("member_id", "checkout_key", name="uq_order_member_checkout"),)

    order_no = Column(String(32), nullable=False, comment="订单编号", index=True)
    member_id = Column(BigInteger, nullable=True, comment="下单用户ID", index=True)
    username = Column(String(64), nullable=True, comment="下单用户昵称", index=True)
    avatar = Column(Text, nullable=True, comment="用户头像")
    order_time = Column(DateTime, nullable=True, comment="下单时间", index=True)
    status = Column(Integer, nullable=False, default=1, comment="订单状态 1未付款 2用户取消 3系统取消 4已付款 5申请退款 6已退款 7已发货 8用户收货 9系统收货", index=True)
    total_amount = Column(Numeric(12, 2), nullable=True, comment="订单金额")
    pay_amount = Column(Numeric(12, 2), nullable=True, comment="实付金额")
    pay_time = Column(DateTime, nullable=True, comment="支付时间")
    pay_channel = Column(String(32), nullable=True, comment="支付渠道")
    goods_amount = Column(Numeric(12, 2), nullable=True, comment="下单时商品金额快照")
    freight_amount = Column(Numeric(12, 2), nullable=True, comment="下单时运费快照")
    discount_amount = Column(Numeric(12, 2), nullable=True, comment="优惠券实际抵扣快照")
    coupon_user_id = Column(BigInteger, nullable=True, comment="使用的会员优惠券ID")
    checkout_key = Column(String(80), nullable=True, comment="会员下单幂等键")

    user_message = Column(String(500), nullable=True, comment="用户留言")

    receiver_name = Column(String(64), nullable=True, comment="收货人", index=True)
    receiver_phone = Column(String(20), nullable=True, comment="收货电话")
    receiver_region = Column(String(255), nullable=True, comment="区域地址")
    receiver_detail = Column(String(255), nullable=True, comment="详细地址")

    express_company = Column(String(64), nullable=True, comment="物流渠道")
    express_no = Column(String(64), nullable=True, comment="物流单号")
    deliver_time = Column(DateTime, nullable=True, comment="发货时间")
    confirm_time = Column(DateTime, nullable=True, comment="确认收货时间")

    refund_amount = Column(Numeric(12, 2), nullable=True, comment="退款金额")
    refund_type = Column(String(32), nullable=True, comment="退款类型")
    refund_note = Column(String(255), nullable=True, comment="退款备注")
    refund_time = Column(DateTime, nullable=True, comment="退款时间")

    @classmethod
    async def get_list(cls, params) -> typing.Dict[str, typing.Any]:
        stmt = cls._build_stmt(params)
        return await cls.pagination(stmt)

    @classmethod
    async def get_all_by_query(cls, params) -> typing.List[typing.Dict[str, typing.Any]]:
        stmt = cls._build_stmt(params)
        return await cls.get_result(stmt) or []

    @classmethod
    def _build_stmt(cls, params):
        q = [cls.enabled_flag.is_(True)]
        if getattr(params, "username", None):
            q.append(cls.username.like("%{}%".format(params.username)))
        if getattr(params, "receiver_name", None):
            q.append(cls.receiver_name.like("%{}%".format(params.receiver_name)))
        if getattr(params, "order_no", None):
            q.append(cls.order_no.like("%{}%".format(params.order_no)))
        if getattr(params, "status", None):
            q.append(cls.status == params.status)
        if getattr(params, "start_time", None):
            q.append(cls.order_time >= params.start_time)
        if getattr(params, "end_time", None):
            q.append(cls.order_time <= params.end_time)
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.order_time.desc(), cls.id.desc())
        )

    @classmethod
    async def get_member_list(cls, params, member_id: int, statuses):
        q = [cls.member_id == member_id, cls.enabled_flag.is_(True)]
        if statuses:
            q.append(cls.status.in_(statuses))
        # 只取列表所需公开快照，幂等键与内部审计字段不返回客户端。
        stmt = select(cls.id, cls.order_no, cls.status, cls.order_time, cls.total_amount).where(*q).order_by(cls.order_time.desc(), cls.id.desc())
        return await cls.parse_pagination(stmt, page=params.page, page_size=params.pageSize)


class OrderItem(Base):
    """商城订单商品明细表 mal_order_item"""

    __tablename__ = "mal_order_item"

    order_id = Column(BigInteger, nullable=False, comment="订单ID", index=True)
    goods_id = Column(BigInteger, nullable=True, comment="下单商品ID快照")
    product_id = Column(BigInteger, nullable=True, comment="下单库存规格ID快照")
    goods_name = Column(String(255), nullable=True, comment="商品名称")
    goods_no = Column(String(64), nullable=True, comment="商品编号")
    spec = Column(String(128), nullable=True, comment="货品规格")
    price = Column(Numeric(12, 2), nullable=True, comment="货品价格")
    quantity = Column(Integer, nullable=True, default=1, comment="货品数量")
    image = Column(Text, nullable=True, comment="货品图片")

    @classmethod
    async def get_by_order_ids(cls, order_ids: typing.List[int]) -> typing.List[typing.Dict[str, typing.Any]]:
        if not order_ids:
            return []
        stmt = (
            select(cls.get_table_columns())
            .where(cls.order_id.in_(order_ids), cls.enabled_flag.is_(True))
            .order_by(cls.id.asc())
        )
        return await cls.get_result(stmt) or []

    @classmethod
    async def get_by_order(cls, order_id: int) -> typing.List[typing.Dict[str, typing.Any]]:
        return await cls.get_by_order_ids([order_id])

    @classmethod
    async def delete_by_order(cls, order_id: int) -> int:
        """物理删除某订单的全部明细"""
        result = await cls.execute(delete(cls).where(cls.order_id == order_id))
        return result.rowcount
