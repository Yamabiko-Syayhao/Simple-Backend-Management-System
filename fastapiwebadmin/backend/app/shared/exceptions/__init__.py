# -*- coding: utf-8 -*-
"""业务异常定义"""
from app.shared.exceptions.errors import (
    MyBaseException,
    IpError,
    SetRedis,
    IdNotExist,
    UserNotExist,
    ErrorUser,
    ParameterError,
    AccessTokenFail,
    PermissionNotEnough,
)

__all__ = [
    "MyBaseException",
    "IpError",
    "SetRedis",
    "IdNotExist",
    "UserNotExist",
    "ErrorUser",
    "ParameterError",
    "AccessTokenFail",
    "PermissionNotEnough",
]
