# -*- coding: utf-8 -*-
"""会员管理接口层"""

from urllib.parse import quote

from fastapi import Depends, File, UploadFile
from starlette.responses import StreamingResponse

from app.api.v1.system.member.schema import (
    MemberDel,
    MemberIn,
    MemberLoginIn,
    MemberMobileIn,
    MemberProfileIn,
    MemberQuery,
    MemberRegisterIn,
)
from app.api.v1.system.member.service import MemberService
from app.core.dependencies import AuthPermission
from app.shared.router import APIRouter
from app.utils.response import HttpResponse

MemberRouter = APIRouter(prefix="/member", tags=["会员管理"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# ============================================================ 管理后台
@MemberRouter.post("/list", description="会员列表")
async def member_list(params: MemberQuery, _auth=Depends(AuthPermission(["member:query"]))):
    data = await MemberService.list(params)
    return await HttpResponse.success(data)


@MemberRouter.post("/detail", description="会员详情")
async def member_detail(
    params: MemberDel,
    _auth=Depends(AuthPermission(["member:query"], check_data_scope=False)),
):
    data = await MemberService.detail(params.id)
    return await HttpResponse.success(data)


@MemberRouter.post("/saveOrUpdate", description="新增或编辑会员")
async def member_save_or_update(
    params: MemberIn,
    _auth=Depends(AuthPermission(["member:add", "member:edit"])),
):
    await MemberService.save_or_update(params)
    return await HttpResponse.success()


@MemberRouter.post("/deleted", description="删除会员")
async def member_deleted(params: MemberDel, _auth=Depends(AuthPermission(["member:delete"]))):
    await MemberService.deleted(params.id)
    return await HttpResponse.success()


@MemberRouter.post("/export", description="导出会员列表 xlsx")
async def member_export(
    params: MemberQuery,
    _auth=Depends(AuthPermission(["member:export"], check_data_scope=False)),
):
    content, filename = await MemberService.export(params)
    headers = {
        "Content-Disposition": (
            "attachment; filename=member.xlsx; "
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    return StreamingResponse(iter([content]), media_type=XLSX_MEDIA_TYPE, headers=headers)


# ============================================================ 客户端（H5 / 小程序）
@MemberRouter.post("/login", description="会员登录（客户端）")
async def member_login(params: MemberLoginIn):
    data = await MemberService.login(params)
    return await HttpResponse.success(data, msg="登录成功！")


@MemberRouter.post("/register", description="会员注册（客户端）")
async def member_register(params: MemberRegisterIn):
    await MemberService.register(params)
    return await HttpResponse.success(msg="注册成功")


@MemberRouter.post("/profile", description="当前登录会员信息（客户端）")
async def member_profile():
    data = await MemberService.profile()
    return await HttpResponse.success(data)


@MemberRouter.post("/updateProfile", description="修改本人昵称与性别（客户端）")
async def member_update_profile(params: MemberProfileIn):
    data = await MemberService.update_profile(params)
    return await HttpResponse.success(data)


@MemberRouter.post("/uploadAvatar", description="上传并保存本人头像（客户端，不超过3MB）")
async def member_upload_avatar(file: UploadFile = File(...)):
    data = await MemberService.upload_avatar(file)
    return await HttpResponse.success(data)


@MemberRouter.post("/changeMobile", description="校验当前密码后修改本人手机号（客户端）")
async def member_change_mobile(params: MemberMobileIn):
    data = await MemberService.change_mobile(params)
    return await HttpResponse.success(data)


@MemberRouter.post("/logout", description="会员退出登录（客户端）")
async def member_logout():
    await MemberService.logout()
    return await HttpResponse.success()
