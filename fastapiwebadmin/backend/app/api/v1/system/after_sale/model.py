# -*- coding: utf-8 -*-
"""售后管理数据层"""

import typing

from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, String, select

from app.models.base import Base


class AfterSale(Base):
    """售后申请表 mal_after_sale

    数据来源：客户端用户点击「申请退款 / 退货退款」后写入，后台在这里审核。
    """

    __tablename__ = "mal_after_sale"

    after_sale_no = Column(String(32), nullable=False, comment="售后编号", index=True)
    order_id = Column(BigInteger, nullable=False, comment="订单ID", index=True)
    order_no = Column(String(32), nullable=True, comment="订单编号")
    member_id = Column(BigInteger, nullable=True, comment="用户ID", index=True)
    username = Column(String(64), nullable=True, comment="用户昵称")
    type = Column(String(32), nullable=True, comment="售后类型，如：仅退款 / 退货退款")
    reason = Column(String(500), nullable=True, comment="退款原因")
    refund_amount = Column(Numeric(12, 2), nullable=True, comment="退款价格")
    status = Column(Integer, nullable=False, default=1, comment="状态 1待审核 2待退款 3已拒绝 4已退款", index=True)
    apply_time = Column(DateTime, nullable=True, comment="申请时间", index=True)
    audit_time = Column(DateTime, nullable=True, comment="审核时间")
    audit_remark = Column(String(255), nullable=True, comment="审核备注")

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
        if getattr(params, "after_sale_no", None):
            q.append(cls.after_sale_no.like("%{}%".format(params.after_sale_no)))
        if getattr(params, "order_id", None):
            q.append(cls.order_id == params.order_id)
        if getattr(params, "status", None):
            q.append(cls.status == params.status)
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.apply_time.desc(), cls.id.desc())
        )
