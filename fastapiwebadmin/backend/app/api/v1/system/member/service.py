# -*- coding: utf-8 -*-
"""会员业务层"""

import typing
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from app.api.v1.common.file.model import FileInfo
from app.api.v1.common.file.service import FileService
from app.api.v1.system.cart.service import CartService
from app.api.v1.system.member.model import Member
from app.api.v1.system.member.schema import (
    MemberIn,
    MemberLoginIn,
    MemberMobileIn,
    MemberProfileIn,
    MemberQuery,
    MemberRegisterIn,
)
from app.database import redis_pool
from app.database.sqlalchemy import async_session_factory
from app.shared.constants.consts import CACHE_DAY, TEST_USER_INFO
from app.utils.context import FastApiRequest
from app.utils.security import hash_password, verify_password
from app.utils.serialize import default_serialize
from app.utils.storage import StorageFactory

DEFAULT_PASSWORD = "123456"

GENDER_TEXT = {0: "未知", 1: "男", 2: "女"}
LEVEL_TEXT = {0: "普通用户", 1: "高级VIP用户"}
STATUS_TEXT = {1: "可用", 2: "禁用", 0: "注销"}

EXPORT_HEADERS = ["用户ID", "用户昵称", "手机号码", "性别", "生日", "用户等级", "状态", "注册时间"]
MAX_AVATAR_BYTES = 3 * 1024 * 1024
AVATAR_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "webp"}


class MemberService:
    """会员管理"""

    # ------------------------------------------------------------------ 通用
    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """补充前端直接展示的中文文案字段"""
        gender = row.get("gender")
        level = row.get("level")
        status = row.get("status")
        row["gender_name"] = GENDER_TEXT.get(gender, "未知")
        row["level_name"] = LEVEL_TEXT.get(level, "普通用户")
        row["status_name"] = STATUS_TEXT.get(status, "可用")
        return row

    # ------------------------------------------------------------------ 后台：列表 / 详情
    @staticmethod
    async def list(params: MemberQuery) -> typing.Dict[str, typing.Any]:
        data = await Member.get_list(params)
        for row in data.get("rows", []):
            MemberService._decorate(row)
        return data

    @staticmethod
    async def detail(member_id: int) -> typing.Dict[str, typing.Any]:
        member = await Member.get(member_id, to_dict=True)
        if not member:
            raise ValueError("会员不存在")
        member.pop("password", None)
        return MemberService._decorate(member)

    # ------------------------------------------------------------------ 后台：新增 / 编辑 / 删除
    @staticmethod
    async def save_or_update(params: MemberIn) -> typing.Dict[str, typing.Any]:
        payload = params.model_dump()

        if not payload.get("id"):
            if not payload.get("username"):
                raise ValueError("登录账号不能为空")
            if await Member.get_by_username(payload["username"]):
                raise ValueError("登录账号已存在")
            payload["password"] = hash_password(payload.get("password") or DEFAULT_PASSWORD)
            await Member.create(payload)
            return {}

        current = await Member.get(payload["id"], to_dict=True)
        if not current:
            raise ValueError("会员不存在")

        password = payload.pop("password", None)
        if password:
            payload["password"] = (
                password if password.startswith(("$2a$", "$2b$")) else hash_password(password)
            )
        await Member.update(payload)
        return {}

    @staticmethod
    async def deleted(member_id: int) -> int:
        return await Member.delete(member_id, True)

    # ------------------------------------------------------------------ 后台：导出 xlsx
    @staticmethod
    async def export(params: MemberQuery) -> tuple[bytes, str]:
        rows = await Member.get_all_by_query(params)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "会员列表"

        header_fill = PatternFill("solid", fgColor="F2F5F8")
        header_font = Font(bold=True, color="333333")
        center = Alignment(horizontal="center", vertical="center")

        sheet.append(EXPORT_HEADERS)
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center

        for row in rows:
            sheet.append(
                [
                    row.get("id"),
                    row.get("nickname") or "",
                    row.get("mobile") or "",
                    GENDER_TEXT.get(row.get("gender"), "未知"),
                    default_serialize(row.get("birthday")) or "",
                    LEVEL_TEXT.get(row.get("level"), "普通用户"),
                    STATUS_TEXT.get(row.get("status"), "可用"),
                    row.get("creation_date") or "",
                ]
            )

        widths = [12, 18, 18, 8, 14, 16, 8, 22]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"会员列表_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"

    # ------------------------------------------------------------------ C 端：登录 / 注册 / 个人信息
    @staticmethod
    async def create_login_session(member: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """创建会员登录会话。

        注意：会话里刻意不写 ``id`` 字段，只写 ``member_id``，
        这样会员 token 无法通过后台接口的 AuthPermission（它按 ``id`` 查 sys_user），
        避免会员 token 被当成后台管理员使用。
        """
        token = str(uuid.uuid4())
        token_info = {
            "token": token,
            "login_time": default_serialize(datetime.now()),
            "username": member["username"],
            "nickname": member.get("nickname"),
            "member_id": member["id"],
            "user_type": "member",
        }
        await redis_pool.redis.set(TEST_USER_INFO.format(token), token_info, CACHE_DAY)
        return token_info

    @staticmethod
    async def login(params: MemberLoginIn) -> typing.Dict[str, typing.Any]:
        member = await Member.get_by_username(params.username)
        if not member:
            raise ValueError("账号或密码错误")
        if not verify_password(params.password, member.get("password") or ""):
            raise ValueError("账号或密码错误")
        if member.get("status") == 0:
            raise ValueError("该账号已注销，请联系客服")
        if member.get("status") == 2:
            raise ValueError("该账号已被禁用，请联系客服")

        token_info = await MemberService.create_login_session(member)
        return {
            "token": token_info["token"],
            "username": token_info["username"],
            "nickname": token_info["nickname"],
            "member_id": token_info["member_id"],
            "login_time": token_info["login_time"],
        }

    @staticmethod
    async def register(params: MemberRegisterIn) -> None:
        if await Member.get_by_username(params.username):
            raise ValueError("登录账号已被注册")
        if params.mobile and await Member.get_by_mobile(params.mobile):
            raise ValueError("手机号已被注册")
        await Member.create(
            {
                "username": params.username,
                "password": hash_password(params.password),
                "nickname": params.nickname or params.username,
                "mobile": params.mobile,
                "gender": 0,
                "level": 0,
                "status": 1,
            }
        )

    @staticmethod
    async def profile() -> typing.Dict[str, typing.Any]:
        member_id = await CartService._member_id()
        async with async_session_factory() as session:
            member = await CartService._member(session, member_id)
            return MemberService._client_profile(member)

    @staticmethod
    def _client_profile(member: Member) -> typing.Dict[str, typing.Any]:
        """客户端只返回业务展示字段，不暴露密码和后台审计字段。"""
        return MemberService._decorate({
            "id": member.id, "member_id": member.id, "username": member.username,
            "nickname": member.nickname or "", "avatar": member.avatar or "",
            "mobile": member.mobile or "", "gender": member.gender,
            "birthday": member.birthday, "level": member.level, "status": member.status,
        })

    @staticmethod
    async def update_profile(params: MemberProfileIn) -> typing.Dict[str, typing.Any]:
        member_id = await CartService._member_id()
        payload = params.model_dump(exclude_unset=True)
        if not payload or any(value is None for value in payload.values()):
            raise ValueError("请选择要修改的信息，昵称不能为空")
        nickname = payload.get("nickname")
        if nickname is not None and (not nickname.strip() or any(ord(c) < 32 for c in nickname)):
            raise ValueError("昵称不能为空或包含控制字符")
        async with async_session_factory() as session, session.begin():
            member = await CartService._member(session, member_id, lock=True)
            for field, value in payload.items():
                setattr(member, field, value)
            await session.flush()
            return MemberService._client_profile(member)

    @staticmethod
    async def change_mobile(params: MemberMobileIn) -> typing.Dict[str, typing.Any]:
        member_id = await CartService._member_id()
        for attempt in range(3):
            try:
                async with async_session_factory() as session, session.begin():
                    member = await CartService._member(session, member_id, lock=True)
                    if not verify_password(params.password, member.password or ""):
                        raise ValueError("当前登录密码不正确")
                    # MySQL 手机号索引的锁定读覆盖空范围，防止两个会员同时绑定同一新号码。
                    occupied = await session.scalar(select(Member.id).where(
                        Member.mobile == params.mobile, Member.id != member_id, Member.enabled_flag.is_(True)
                    ).with_for_update())
                    if occupied:
                        raise ValueError("手机号已被其他账号使用")
                    member.mobile = params.mobile
                    await session.flush()
                    return MemberService._client_profile(member)
            except OperationalError as exc:
                # 并发空范围更新可能选中本事务为死锁牺牲者；回滚后重试并重新核对归属。
                if getattr(exc.orig, "args", (None,))[0] not in (1205, 1213):
                    raise
                if attempt == 2:
                    raise ValueError("手机号修改请求繁忙，请稍后重试") from exc

    @staticmethod
    def _avatar_content_matches(extension: str, content: bytes) -> bool:
        """文件头须与图片扩展名相符；不接受可执行脚本类 SVG。"""
        if extension in {"jpg", "jpeg"}:
            return content.startswith(b"\xff\xd8\xff") and content.rstrip().endswith(b"\xff\xd9")
        if extension == "png":
            return content.startswith(b"\x89PNG\r\n\x1a\n") and b"IHDR" == content[12:16] and content.endswith(b"IEND\xaeB`\x82")
        if extension == "gif":
            return content[:6] in {b"GIF87a", b"GIF89a"} and content.rstrip().endswith(b";")
        if extension == "bmp":
            return len(content) >= 26 and content[:2] == b"BM"
        return extension == "webp" and len(content) >= 20 and content[:4] == b"RIFF" and content[8:12] == b"WEBP"

    @staticmethod
    async def upload_avatar(file: UploadFile) -> typing.Dict[str, typing.Any]:
        member_id = await CartService._member_id()
        async with async_session_factory() as session:
            await CartService._member(session, member_id)
        extension = Path(file.filename or "").suffix.lower().lstrip(".")
        if extension not in AVATAR_EXTENSIONS or len(file.filename or "") > 255:
            raise ValueError("头像支持 jpg / jpeg / png / gif / bmp / webp 图片")
        content_type = (file.content_type or "").lower()
        if content_type not in {"", "application/octet-stream"} and not content_type.startswith("image/"):
            raise ValueError("请选择图片作为头像")
        content = await file.read(MAX_AVATAR_BYTES + 1)
        await file.seek(0)
        if not content or len(content) > MAX_AVATAR_BYTES:
            raise ValueError("头像须大于0且大小不能超过3MB")
        if not MemberService._avatar_content_matches(extension, content):
            raise ValueError("图片内容与文件格式不匹配，请重新选择头像")
        uploaded = None
        try:
            async with async_session_factory() as session, session.begin():
                member = await CartService._member(session, member_id, lock=True)
                # 上传与本人绑定，前端不能提交外部 URL 或其他会员的文件 ID 作为头像。
                uploaded = await FileService.upload(file, f"members/{member_id}/avatars")
                member.avatar = uploaded["url"]
                await session.flush()
                result = {**uploaded, "profile": MemberService._client_profile(member)}
            return result
        except Exception:
            if uploaded:
                info = await FileInfo.get(uploaded["id"], to_dict=True)
                if info:
                    await StorageFactory.create(info.get("storage_type") or "local").delete(info["file_path"])
                    await FileInfo.delete(uploaded["id"], True)
            raise

    @staticmethod
    async def logout() -> None:
        request = FastApiRequest.get()
        token = request.headers.get("token")
        if token:
            await redis_pool.redis.delete(TEST_USER_INFO.format(token))
