import asyncio
import time
import traceback
import typing
import uuid
from datetime import datetime

from loguru import logger

from app.shared import g
from app.shared.constants.codes import CodeEnum
from app.shared.constants.consts import TEST_USER_INFO, CACHE_DAY
from app.database import redis_pool
from app.api.v1.system.menu.model import Menu
from app.api.v1.system.user.model import User, UserRole
from app.api.v1.system.login_record.model import UserLoginRecord
from app.api.v1.system.login_record.schema import LoginRecordIn
from app.api.v1.system.user.schema import UserLogin, UserIn, UserResetPwd, UserDel, UserQuery
from app.api.v1.system.menu.service import MenuService
from app.api.v1.system.auth.service import CaptchaService
from app.core.permission import PermissionService
from app.utils.context import FastApiRequest
from app.utils.current_user import current_user
from app.utils.des import encrypt_rsa_password, decrypt_rsa_password
from app.utils.security import hash_password
from app.utils.serialize import default_serialize


class UserService:
    """用户类"""

    @staticmethod
    def _normalize_user_payload(payload: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
      
        if payload.get("avatar") is None:
            payload["avatar"] = ""
        if payload.get("tags") is None:
            payload["tags"] = []
        if payload.get("remarks") is None:
            payload["remarks"] = ""
        return payload

    @staticmethod
    async def create_login_session(user: typing.Union[User, typing.Dict[str, typing.Any]]) -> typing.Dict[str, typing.Any]:
        """创建 Redis 登录会话。"""
        if isinstance(user, User):
            role_ids = await UserRole.get_role_ids_by_user(user.id)
            user_info = {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "roles": role_ids,
                "tags": user.tags or [],
            }
        else:
            user_info = dict(user)
            if user_info.get("id") and "roles" not in user_info:
                user_info["roles"] = await UserRole.get_role_ids_by_user(user_info["id"])

        token = str(uuid.uuid4())
        login_time = default_serialize(datetime.now())
        token_user_info = {
            "id": user_info["id"],
            "token": token,
            "login_time": login_time,
            "username": user_info["username"],
            "nickname": user_info.get("nickname"),
            "roles": user_info.get("roles") or [],
            "tags": user_info.get("tags") or [],
        }
        await redis_pool.redis.set(TEST_USER_INFO.format(token), token_user_info, CACHE_DAY)
        asyncio.create_task(UserService.login_record("login", token_user_info, token))
        return token_user_info

    @staticmethod
    async def login(params: UserLogin) -> typing.Dict[typing.Text, typing.Any]:
        """
        登录
        :return:
        """
        username = params.username
        password = params.password
        if not username and not password:
            raise ValueError(CodeEnum.PARTNER_CODE_PARAMS_FAIL.msg)

        await CaptchaService.verify_captcha(params.captcha_key, params.captcha)

        user_info = await User.get_user_by_name(username)
        if not user_info:
            raise ValueError(CodeEnum.WRONG_USER_NAME_OR_PASSWORD.msg)

        user_status = user_info.get("status")
        if user_status in [0, False, '0', None]:
            raise ValueError('该账户已被禁用，请联系管理员！')

        from app.utils.security import verify_password
        if not verify_password(password, user_info["password"]):
            raise ValueError(CodeEnum.WRONG_USER_NAME_OR_PASSWORD.msg)

        logger.info('用户 [{}] 登录了系统，状态: {}'.format(user_info["username"], user_status))
        user_info["roles"] = await UserRole.get_role_ids_by_user(user_info["id"])
        return await UserService.create_login_session(user_info)

    @staticmethod
    async def logout():
        """
        登出
        :return:
        """
        token = FastApiRequest.get().headers.get('token', None)
        try:
            token_user_info = await current_user(token)
            await redis_pool.redis.delete(TEST_USER_INFO.format(token))
            asyncio.create_task(UserService.login_record("logout", token_user_info, token))
        except Exception as err:
            logger.error(traceback.format_exc())

    @staticmethod
    async def login_record(record_type: str, user_token_info: dict, token: str):
        try:
            from app.utils.context import FastApiRequest
            from app.utils.request_meta import resolve_client_ip, resolve_login_location, resolve_user_agent

            request = FastApiRequest.get()
            login_ip = resolve_client_ip(request)
            browser, os_name = resolve_user_agent(request)
            location = resolve_login_location(login_ip)
            source_type = f"{browser} / {os_name}".strip(" /")

            if record_type == 'login':
                params = LoginRecordIn(
                    token=token,
                    code=user_token_info["username"],
                    user_id=user_token_info["id"],
                    user_name=user_token_info["nickname"],
                    login_type="password",
                    login_time=user_token_info['login_time'],
                    login_ip=login_ip,
                    address=location,
                    source_type=source_type or None,
                    ret_code="0",
                    ret_msg="登录成功"
                )
                await UserLoginRecord.create_or_update(params.model_dump())
            elif record_type == 'logout':
                login_recode = await UserLoginRecord.get_by_token(token)
                if login_recode:
                    await UserLoginRecord.update({"id": login_recode['id'], "logout_time": datetime.now()})

        except Exception as exc:
            logger.error(f"登录日志记录错误\n{traceback.format_exc(3)}")

    @staticmethod
    async def user_register(user_params: UserIn) -> "User":
        """用户注册"""
        user_info = await User.get_user_by_name(user_params.username)
        if user_info:
            raise ValueError(CodeEnum.USERNAME_OR_EMAIL_IS_REGISTER.msg)
        payload = UserService._normalize_user_payload(user_params.model_dump())
        role_ids = payload.pop("roles", None) or []
        user = await User.create(payload)
        user_id = user.id if hasattr(user, "id") else user.get("id")
        await UserRole.set_user_roles(user_id, role_ids)
        return user

    @staticmethod
    async def list(params: UserQuery) -> typing.Dict[typing.Text, typing.Any]:
        """
        获取用户列表
        :param params:  查询参数
        :return:
        """
        data = await User.get_list(params)
        user_ids = [row["id"] for row in data.get("rows", [])]
        role_map = await UserRole.get_role_ids_map(user_ids)
        for row in data.get("rows", []):
            row["roles"] = role_map.get(row["id"], [])
            row["tags"] = row.get("tags") or []
        return data

    @staticmethod
    async def save_or_update(params: UserIn) -> typing.Dict[typing.Text, typing.Any]:
        """
        用户保存方法
        :param params: 用户字段
        :return:
        """
        if not params.id:
            # 新建用户
            if await User.get_user_by_nickname(params.nickname):
                raise ValueError('用户昵称已存在！')
            # 新建用户时，如果没有提供密码，使用默认密码
            if not params.password:
                params.password = '123456'  # 默认密码
            # 密码加密
            params.password = hash_password(params.password)
            payload = UserService._normalize_user_payload(params.model_dump())
            # 新增时补默认值，避免 status/user_type 为 None 触发数据库非空约束
            if payload.get("status") is None:
                payload["status"] = 1
            if payload.get("user_type") is None:
                payload["user_type"] = 20
        else:
            # 更新用户
            user_info = await User.get(params.id, to_dict=True)
            if not user_info:
                raise ValueError('用户不存在！')
            if user_info['nickname'] != params.nickname and await User.get_user_by_nickname(params.nickname):
                raise ValueError('用户昵称已存在！')

            # 仅写入已提交的字段，避免个人资料更新覆盖并发的权限或密码更新。
            payload = params.model_dump(exclude_unset=True, exclude_none=True)
            if params.password and params.password.strip() and not params.password.startswith('$2b$'):
                payload["password"] = hash_password(params.password)
            else:
                payload.pop("password", None)

        role_ids = payload.pop("roles", None)
        if params.id:
            result = await User.update(payload, to_dict=True)
            if not result:
                raise ValueError('用户不存在！')
        else:
            result = await User.create(payload, to_dict=True)
        if role_ids is not None:
            await UserRole.set_user_roles(result["id"], role_ids)
        result["roles"] = await UserRole.get_role_ids_by_user(result["id"])

        current_user_info = await current_user()
        if current_user_info.get("id") == params.id:
            token_user_info = {
                "id": result["id"],
                "token": current_user_info.get("token"),
                "login_time": current_user_info.get("login_time"),
                "username": result["username"],
                "roles": result["roles"],
                "tags": result["tags"]
            }
            await redis_pool.redis.set(TEST_USER_INFO.format(g.token), token_user_info, CACHE_DAY)
        return result

    @staticmethod
    async def deleted(params: UserDel):
        """
        删除用户
        :param params: 删除参数
        :return:
        """
        try:
            await UserRole.delete_by_user(params.id)
            return await User.delete(params.id)
        except Exception as err:
            logger.error(traceback.format_exc())

    @staticmethod
    async def check_token(token: str) -> typing.Dict[typing.Text, typing.Any]:
        """
        校验token
        :param token: token
        :return:
        """
        user_info = await redis_pool.redis.get(TEST_USER_INFO.format(token))
        if not user_info:
            raise ValueError(CodeEnum.PARTNER_CODE_TOKEN_EXPIRED_FAIL.msg)

        user_info = {
            'id': user_info.get('id', None),
            'username': user_info.get('username', None)
        }
        return user_info

    @staticmethod
    async def reset_password(params: UserResetPwd):
        """用户修改自己的密码"""
        if params.new_pwd != params.re_new_pwd:
            raise ValueError(CodeEnum.PASSWORD_TWICE_IS_NOT_AGREEMENT.msg)
        
        user_info = await User.get(params.id, to_dict=True)
        if not user_info:
            raise ValueError('用户不存在！')
        
        # 使用 bcrypt 验证旧密码
        from app.utils.security import verify_password
        if not verify_password(params.old_pwd, user_info['password']):
            raise ValueError(CodeEnum.OLD_PASSWORD_ERROR.msg)
        
        # 检查新密码是否与旧密码相同
        if verify_password(params.new_pwd, user_info['password']):
            raise ValueError(CodeEnum.NEW_PWD_NO_OLD_PWD_EQUAL.msg)
        
        # 加密新密码
        new_pwd_hash = hash_password(params.new_pwd)
        await User.update({"password": new_pwd_hash, "id": params.id})
        logger.info(f'用户 [{user_info["username"]}] 修改了密码')

    @staticmethod
    async def admin_reset_password(user_id: int, new_password: str = '123456'):
        """管理员重置用户密码"""
        user_info = await User.get(user_id)
        if not user_info:
            raise ValueError('用户不存在！')
        
        # 加密新密码
        hashed_password = hash_password(new_password)
        await User.update({"password": hashed_password, "id": user_id})
        logger.info(f'管理员重置用户 [{user_info.username}] 的密码')
        return True

    @staticmethod
    async def update_user_avatar(user_id: int, avatar: str):
        """更新用户头像。

        头像允许三种形式：base64 data URL、后端文件地址（/api/files/...）、http(s) 链接。
        前端裁剪后统一压到 200x200，正常在 30KB 以内；这里再做一次兜底校验，
        避免超大字符串直接打到数据库。
        """
        user_info = await User.get(user_id)
        if not user_info:
            raise ValueError('用户不存在！')

        value = (avatar or "").strip()
        if value:
            allowed = value.startswith("data:image/") or value.startswith("/") or value.startswith("http://") \
                or value.startswith("https://")
            if not allowed:
                raise ValueError('头像格式不支持，请重新选择图片')
            if len(value) > 800_000:
                raise ValueError('头像图片过大，请重新选择（建议 200x200 以内）')

        await User.update({"avatar": value, "id": user_id})
        logger.info(f'用户 [{user_info.username}] 更新了头像')
        return True

    @staticmethod
    async def get_user_info(user_id: int):
        """获取用户信息"""
        user_info = await User.get(user_id, to_dict=True)
        if not user_info:
            raise ValueError('用户不存在！')
        user_info["roles"] = await UserRole.get_role_ids_by_user(user_id)
        return user_info

    @staticmethod
    async def get_button_permissions() -> typing.List[str]:
        """根据 token 获取当前用户按钮权限码。"""
        token_user_info = await current_user()
        if not token_user_info:
            raise ValueError(CodeEnum.PARTNER_CODE_TOKEN_EXPIRED_FAIL.msg)
        user_info = await User.get(token_user_info.get("id"))
        if not user_info:
            raise ValueError(CodeEnum.PARTNER_CODE_TOKEN_EXPIRED_FAIL.msg)
        return await PermissionService.get_permission_codes(user_info)

    @staticmethod
    async def get_user_info_by_token() -> typing.Union[typing.Dict[typing.Text, typing.Any], None]:
        """根据token获取用户信息"""
        token_user_info = await current_user()
        if not token_user_info:
            raise ValueError(CodeEnum.PARTNER_CODE_TOKEN_EXPIRED_FAIL.msg)
        user_info = await User.get(token_user_info.get("id"))
        if not user_info:
            raise ValueError(CodeEnum.PARTNER_CODE_TOKEN_EXPIRED_FAIL.msg)

        auth_btn_list = await PermissionService.get_permission_codes(user_info)
        role_ids = await UserRole.get_role_ids_by_user(user_info.id)

        return {
            "id": user_info.id,
            "avatar": user_info.avatar,
            "username": user_info.username,
            "nickname": user_info.nickname,
            "roles": role_ids,
            "tags": user_info.tags,
            "user_type": user_info.user_type,
            "login_time": token_user_info.get("login_time", None),
            "authBtnList": auth_btn_list,
        }

    @staticmethod
    async def get_menu_by_token() -> typing.List[typing.Dict[typing.Text, typing.Any]]:
        """获取用户菜单权限"""
        current_user_info = await current_user()
        if not current_user_info:
            return []
        user_info = await User.get(current_user_info.get("id"))
        if not user_info:
            return []
        menu_ids = await PermissionService.get_menu_ids_for_user(user_info)
        if not menu_ids:
            return []
        parent_menus = await Menu.get_parent_id_by_ids(list(set(menu_ids)))
        menu_ids += [i["parent_id"] for i in parent_menus]
        all_menu = await Menu.get_menu_by_ids(list(set(menu_ids)))
        all_menu = [menu for menu in all_menu if menu.get("menu_type") != 20]
        parent_menu = [menu for menu in all_menu if menu['parent_id'] == 0]
        return MenuService.menu_assembly(parent_menu, all_menu)
