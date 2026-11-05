# -*- coding: utf-8 -*-
"""售后管理 Pydantic 契约层"""

from typing import List, Optional

from pydantic import BaseModel

from app.shared.schemas.base import BaseSchema


class AfterSaleQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 20
    after_sale_no: Optional[str] = None
    order_id: Optional[int] = None
    status: Optional[int] = None


class AfterSaleAuditIn(BaseSchema):
    """批量通过 / 批量拒绝"""

    ids: Optional[List[int]] = None
    action: Optional[str] = None  # pass / reject
    remark: Optional[str] = None


class AfterSaleDel(BaseModel):
    """详情"""

    id: int
