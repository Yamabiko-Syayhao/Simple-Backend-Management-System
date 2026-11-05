# -*- coding: utf-8 -*-
"""收货地址 Pydantic 契约层"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

from app.shared.schemas.base import BaseSchema


class AddressQuery(BaseSchema):
    """列表 / 导出查询条件"""

    page: int = 1
    pageSize: int = 10
    member_id: Optional[int] = None
    receiver_name: Optional[str] = None
    # 服务端排序：asc / desc（默认 desc），由前端表头排序触发
    sort_order: Optional[str] = None


class AddressIn(BaseSchema):
    """新增 / 编辑收货地址"""

    id: Optional[int] = None
    member_id: Optional[int] = None
    receiver_name: Optional[str] = None
    mobile: Optional[str] = None
    region: Optional[str] = None
    detail: Optional[str] = None
    is_default: Optional[int] = 0


class AddressDel(BaseModel):
    """删除 / 详情"""

    id: int


class AddressClientSchema(BaseSchema):
    """会员身份与区域文字均由服务端确定。"""

    model_config = ConfigDict(extra="forbid")


class AddressClientQuery(AddressClientSchema):
    pass


class AddressClientId(AddressClientSchema):
    id: int = Field(gt=0)


class AddressClientIn(AddressClientSchema):
    id: Optional[int] = Field(default=None, gt=0)
    receiver_name: str = Field(min_length=1, max_length=64)
    mobile: str = Field(pattern=r"^1[3-9]\d{9}$")
    region_ids: list[int] = Field(min_length=3, max_length=3)
    detail: str = Field(min_length=1, max_length=255)
    is_default: StrictBool = False

    @field_validator("receiver_name", "mobile", "detail", mode="before")
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("region_ids")
    @classmethod
    def valid_region_ids(cls, value):
        if len(value) != 3 or any(i <= 0 for i in value) or len(set(value)) != 3:
            raise ValueError("请选择完整的省市区")
        return value
