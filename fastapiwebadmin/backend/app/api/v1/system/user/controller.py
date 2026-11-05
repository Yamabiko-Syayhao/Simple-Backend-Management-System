# -*- coding: utf-8 -*-
# @author: rebort
from fastapi import Depends
from fastapi.requests import Request

from app.core.dependencies import AuthPermission
from app.shared.constants.codes import CodeEnum
from app.shared.router import APIRouter
from app.api.v1.system.user.schema import UserLogin, UserQuery, UserIn, UserResetPwd, UserDel, UserUpdateAvatar
from app.api.v1.system.user.service import UserService
from app.utils.current_user import current_user
from app.utils.response import HttpResponse

UserRouter = APIRouter(prefix="/user", tags=["用户管理"])
_PROFILE_FIELDS = {"id", "username", "nickname", "avatar", "remarks", "email", "tags"}


@UserRouter.post("/login", description="登录")
async def login(params: UserLogin):
    data = await UserService.login(params)
    return await HttpResponse.success(data, msg="登录成功！")


@UserRouter.post("/logout", description="登出")
async def logout():
    await UserService.logout()
    return await HttpResponse.success()


@UserRouter.post("/list", description="用户列表")
async def user_list(params: UserQuery, _auth=Depends(AuthPermission(["user:query"]))):
    data = await UserService.list(params)
    return await HttpResponse.success(data)


@UserRouter.post('/saveOrUpdate', description="更新保存用户")
async def save_or_update(user_params: UserIn):
    """本人可以保存个人资料，修改账号管理字段需要编辑权限。"""
    token_user = await current_user()
    if not user_params.id or token_user.get("id") != user_params.id:
        await AuthPermission(["user:add", "user:edit"])()
    elif user_params.model_fields_set - _PROFILE_FIELDS:
        await AuthPermission(["user:edit"])()

    await UserService.save_or_update(user_params)
    return await HttpResponse.success()


@UserRouter.post('/getUserInfoByToken', description="通过token获取用户信息")
async def get_user_info():
    """
    根据token获取用户信息
    :return:
    """
    user_info = await UserService.get_user_info_by_token()
    return await HttpResponse.success(user_info)


@UserRouter.post('/userRegister', description="新增用户")
async def user_register(user_info: UserIn, _auth=Depends(AuthPermission(["user:add"]))):
    data = await UserService.user_register(user_info)
    return await HttpResponse.success(data)


@UserRouter.post('/resetPassword', description="修改密码")
async def reset_password(params: UserResetPwd):
    await UserService.reset_password(params)
    return await HttpResponse.success()


@UserRouter.post('/adminResetPassword', description="管理员重置用户密码")
async def admin_reset_password(
    params: UserDel,
    _auth=Depends(AuthPermission(["user:resetpwd", "user:resetPwd"])),
):
    """
    管理员重置用户密码为默认密码 123456
    :param params: 包含用户 id
    :return:
    """
    await UserService.admin_reset_password(params.id)
    return await HttpResponse.success(msg='密码已重置为：123456')


@UserRouter.post('/updateUserAvatar', description="更新用户头像")
async def update_user_avatar(params: UserUpdateAvatar):
    """更新用户头像：本人可改自己的头像，改他人需要 user:edit 权限。"""
    from app.utils.current_user import current_user

    token_user = await current_user()
    if not token_user or token_user.get("id") != params.id:
        await AuthPermission(["user:edit"])()

    await UserService.update_user_avatar(params.id, params.avatar)
    return await HttpResponse.success(msg='头像更新成功')


@UserRouter.post('/getUserInfo', description="获取用户信息")
async def get_user_info(
    params: UserDel,
    _auth=Depends(AuthPermission(["user:query"], check_data_scope=False)),
):
    """
    根据用户 id 获取用户信息
    :param params: 包含用户 id
    :return:
    """
    user_info = await UserService.get_user_info(params.id)
    return await HttpResponse.success(user_info)


@UserRouter.post('/deleted', description="删除用户")
async def deleted(params: UserDel, _auth=Depends(AuthPermission(["user:delete"]))):
    data = await UserService.deleted(params)
    return await HttpResponse.success(data)


@UserRouter.post('/authorizeToken', description="校验token是否有效")
async def authorize_token(request: Request):
    token = request.headers.get("token", None)
    user_info = await UserService.check_token(token)
    return await HttpResponse.success(user_info)


@UserRouter.post('/getMenuByToken', description="根据token获取菜单数据")
async def get_menu_by_token():
    user_info = await UserService.get_menu_by_token()
    return await HttpResponse.success(user_info)


@UserRouter.post('/getButtonPermissions', description="根据token获取按钮权限")
async def get_button_permissions():
    permissions = await UserService.get_button_permissions()
    return await HttpResponse.success(permissions)


@UserRouter.post('/debugUserPermissions', description="调试用户权限数据")
async def debug_user_permissions():
    """调试接口：查看用户的完整权限数据"""
    from app.api.v1.system.menu.model import Menu
    from app.api.v1.system.roles.model import RoleMenu, Roles
    from app.api.v1.system.user.model import UserRole
    from app.utils.current_user import current_user
    
    token_user_info = await current_user()
    user_info = await User.get(token_user_info.get("id"))
    role_ids = await UserRole.get_role_ids_by_user(user_info.id)
    
    debug_info = {
        "user": {
            "id": user_info.id,
            "username": user_info.username,
            "user_type": user_info.user_type,
            "user_type_name": "超级管理员" if user_info.user_type == 10 else "普通用户",
            "roles": role_ids,
        },
        "buttons_in_db": [],
        "user_roles": [],
        "assigned_menu_ids": [],
        "assigned_buttons": [],
        "final_auth_list": []
    }
    
    # 1. 查询数据库中所有按钮权限
    all_buttons = await Menu.get_all_buttons()
    debug_info["buttons_in_db"] = [
        {"id": btn.get("id"), "title": btn.get("title"), "roles": btn.get("roles")}
        for btn in all_buttons
    ]
    debug_info["buttons_in_db_count"] = len(all_buttons)
    
    # 2. 获取用户权限
    if user_info.user_type == 10:
        debug_info["final_auth_list"] = [btn.get('roles') for btn in all_buttons if btn.get('roles')]
    else:
        if role_ids:
            roles = await Roles.get_roles_by_ids(role_ids)
            menu_map = await RoleMenu.get_menu_ids_map(role_ids)
            debug_info["user_roles"] = [
                {"id": r.get("id"), "name": r.get("name"), "menus": menu_map.get(r.get("id"), [])}
                for r in roles
            ]
            menu_ids = await RoleMenu.get_menu_ids_by_roles(role_ids)
            debug_info["assigned_menu_ids"] = list(set(menu_ids))
            
            if menu_ids:
                buttons = await Menu.get_buttons_by_ids(list(set(menu_ids)))
                debug_info["assigned_buttons"] = [
                    {"id": btn.get("id"), "title": btn.get("title"), "roles": btn.get("roles")}
                    for btn in buttons
                ]
                debug_info["final_auth_list"] = [btn.get('roles') for btn in buttons if btn.get('roles')]
    
    # 3. 获取完整的用户信息（包含权限）
    full_user_info = await UserService.get_user_info_by_token()
    debug_info["returned_user_info"] = full_user_info
    
    return await HttpResponse.success(debug_info)
