# -*- coding: utf-8 -*-
"""广告管理业务层"""

import typing
from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import select

from app.api.v1.common.file.model import FileInfo
from app.api.v1.common.file.service import FileService
from app.api.v1.system.ad.model import Ad
from app.api.v1.system.ad.schema import AdIn, AdQuery
from app.config.setting import settings

EXPORT_HEADERS = ["广告ID", "广告标题", "广告内容", "广告图片", "广告位置", "活动链接", "是否启用"]
MAX_IMAGE_BYTES = 3 * 1024 * 1024
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "webp", "svg"}


class AdService:
    """广告管理：后台维护，客户端只读取已启用广告"""

    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        row["position_name"] = "首页" if row.get("position") == 1 else ""
        row["status_name"] = "启用" if row.get("status") == 1 else "不启用"
        return row

    @staticmethod
    async def list(params: AdQuery) -> typing.Dict[str, typing.Any]:
        data = await Ad.get_list(params)
        for row in data.get("rows", []):
            AdService._decorate(row)
        return data

    @staticmethod
    async def detail(ad_id: int) -> typing.Dict[str, typing.Any]:
        ad = await Ad.get(ad_id, to_dict=True)
        if not ad:
            raise ValueError("广告不存在")
        return AdService._decorate(ad)

    @staticmethod
    async def save_or_update(params: AdIn) -> typing.Dict[str, typing.Any]:
        payload = params.model_dump()
        for field, label in (("title", "广告标题"), ("content", "广告内容"), ("image", "广告图片")):
            value = (payload.get(field) or "").strip()
            if not value:
                raise ValueError(f"{label}不能为空")
            payload[field] = value
        payload["link"] = (payload.get("link") or "").strip()

        await AdService._validate_image(payload["image"])

        if not payload.get("id"):
            created = await Ad.create(payload, to_dict=True)
            return {"id": created.get("id") if created else None}

        if not await Ad.get(payload["id"]):
            raise ValueError("广告不存在")
        await Ad.update(payload)
        return {"id": payload["id"]}

    @staticmethod
    async def deleted(ad_id: int) -> int:
        if not await Ad.get(ad_id):
            raise ValueError("广告不存在")
        return await Ad.delete(ad_id, True)

    @staticmethod
    async def _validate_image(image: str) -> None:
        """保存时复核图片，通用文件上传的较大附件也不能用于广告。"""
        info = await FileInfo.get_result(
            select(FileInfo.get_table_columns())
            .where(FileInfo.file_url == image, FileInfo.enabled_flag.is_(True))
            .order_by(FileInfo.creation_date.desc()),
            first=True,
        )
        if not info:
            raise ValueError("请先上传广告图片")
        if (info.get("extend_name") or "").lower() not in IMAGE_EXTENSIONS:
            raise ValueError("广告图片格式不支持")
        try:
            size = Decimal(info.get("file_size") or "0") * 1024
        except InvalidOperation:
            raise ValueError("无法确认广告图片大小，请重新上传")
        if not size.is_finite():
            raise ValueError("无法确认广告图片大小，请重新上传")
        if (info.get("storage_type") or "local") == "local":
            root = Path(settings.upload_local_dir).resolve()
            path = (root / (info.get("file_path") or "")).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError("广告图片不存在，请重新上传")
            # 本地直接读真实字节数，避免文件管理的 KB 四舍五入影响 3MB 边界。
            size = path.stat().st_size
        if size <= 0 or size > MAX_IMAGE_BYTES:
            raise ValueError("广告图片须大于 0 且大小不能超过 3MB")

    @staticmethod
    async def upload(file: UploadFile) -> typing.Dict[str, typing.Any]:
        """广告图片单独限制 3MB，存储复用通用文件服务。"""
        extension = Path(file.filename or "").suffix.lower().lstrip(".")
        content_type = file.content_type or ""
        if extension not in IMAGE_EXTENSIONS or (
            content_type not in ("", "application/octet-stream") and not content_type.startswith("image/")
        ):
            raise ValueError("只能上传 jpg / jpeg / png / gif / bmp / webp / svg 图片")
        content = await file.read(MAX_IMAGE_BYTES + 1)
        await file.seek(0)
        if not content:
            raise ValueError("广告图片不能为空")
        if len(content) > MAX_IMAGE_BYTES:
            raise ValueError("广告图片大小不能超过 3MB")
        return await FileService.upload(file, "ads")

    @staticmethod
    async def banners(position: int) -> typing.Dict[str, typing.Any]:
        rows = await Ad.get_banners(position)
        return {"rows": rows, "rowTotal": len(rows)}

    @staticmethod
    async def export(params: AdQuery) -> tuple[bytes, str]:
        rows = await Ad.get_all_by_query(params)
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "广告管理"
        sheet.append(EXPORT_HEADERS)

        center = Alignment(horizontal="center", vertical="center")
        for cell in sheet[1]:
            cell.fill = PatternFill("solid", fgColor="F2F5F8")
            cell.font = Font(bold=True, color="333333")
            cell.alignment = center

        for row in rows:
            AdService._decorate(row)
            sheet.append([
                row.get("id"), row.get("title"), row.get("content"), row.get("image"),
                row.get("position"), row.get("link") or "", row.get("status_name"),
            ])
            for cell in sheet[sheet.max_row]:
                cell.alignment = center
                if isinstance(cell.value, str):
                    cell.data_type = "s"

        for index, width in enumerate([12, 24, 48, 45, 12, 40, 12], start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"广告列表_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
