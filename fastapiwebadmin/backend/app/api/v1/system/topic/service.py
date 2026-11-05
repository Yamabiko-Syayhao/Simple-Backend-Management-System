# -*- coding: utf-8 -*-
"""专题管理业务层"""

import typing
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from html.parser import HTMLParser
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import delete, select

from app.api.v1.system.goods.model import Goods
from app.api.v1.system.topic.model import Topic, TopicGoods
from app.api.v1.system.topic.schema import TopicIn, TopicQuery
from app.database.sqlalchemy import async_session_factory

EXPORT_HEADERS = ["专题ID", "专题标题", "专题子标题", "专题图片", "底价", "阅读数量", "创建时间"]


class _ContentProbe(HTMLParser):
    """识别富文本是否有可见文字或媒体，空段落不算专题内容。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.has_content = False
        self.has_temporary_url = False
        self.ignored = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.ignored += 1
        elif not self.ignored:
            values = dict(attrs)
            if str(values.get("src") or values.get("data") or "").lower().startswith("blob:"):
                self.has_temporary_url = True
            if tag == "hr" or (tag in {"img", "video", "audio", "iframe", "embed", "source"} and values.get("src")):
                self.has_content = True
            elif tag == "object" and values.get("data"):
                self.has_content = True

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.ignored:
            self.ignored -= 1

    def handle_data(self, data):
        if not self.ignored and data.replace("\xa0", "").replace("\u200b", "").strip():
            self.has_content = True


class TopicService:
    """后台编辑专题与商品关联，客户端只读取内容"""

    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        row["price"] = float(row.get("price") or 0)
        count = int(row.get("read_count") or 0)
        if count >= 1000:
            compact = (Decimal(count) / 1000).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            row["read_count_text"] = format(compact, "f").rstrip("0").rstrip(".") + "k"
        else:
            row["read_count_text"] = str(count)
        return row

    @staticmethod
    async def list(params: TopicQuery) -> typing.Dict[str, typing.Any]:
        data = await Topic.get_list(params)
        for row in data.get("rows", []):
            TopicService._decorate(row)
        return data

    @staticmethod
    async def detail(topic_id: int) -> typing.Dict[str, typing.Any]:
        row = await Topic.get(topic_id, to_dict=True)
        if not row:
            raise ValueError("专题不存在")
        goods = await TopicGoods.get_result(
            select(Goods.id, Goods.name, Goods.goods_sn, Goods.image, Goods.brief, Goods.is_on_sale, Goods.retail_price)
            .select_from(TopicGoods)
            .join(Goods, Goods.id == TopicGoods.goods_id)
            .where(TopicGoods.topic_id == topic_id, Goods.enabled_flag.is_(True))
            .order_by(TopicGoods.sort.asc(), TopicGoods.id.asc())
        ) or []
        for product in goods:
            product["retail_price"] = float(product.get("retail_price") or 0)
        row["goods"] = goods
        row["goods_ids"] = [product["id"] for product in goods]
        return TopicService._decorate(row)

    @staticmethod
    async def save_or_update(params: TopicIn) -> typing.Dict[str, typing.Any]:
        payload = params.model_dump(exclude_none=False)
        for field, label in (("title", "专题标题"), ("subtitle", "专题子标题"), ("content", "专题内容")):
            payload[field] = (payload[field] or "").strip()
            if not payload[field]:
                raise ValueError(f"{label}不能为空")
        probe = _ContentProbe()
        probe.feed(payload["content"])
        probe.close()
        if not probe.has_content:
            raise ValueError("专题内容不能为空")
        if probe.has_temporary_url:
            raise ValueError("图片或媒体尚未上传完成，请稍后再保存")
        payload["image"] = (payload.get("image") or "").strip()
        goods_ids = list(dict.fromkeys(payload.pop("goods_ids")))

        async with async_session_factory() as session:
            async with session.begin():
                if goods_ids:
                    found = (await session.scalars(
                        select(Goods.id).where(Goods.id.in_(goods_ids), Goods.enabled_flag.is_(True)).with_for_update()
                    )).all()
                    if len(found) != len(goods_ids):
                        raise ValueError("所选商品不存在，请刷新商品列表后重试")
                if params.id:
                    row = await session.get(Topic, params.id, with_for_update=True)
                    if not row or not row.enabled_flag:
                        raise ValueError("专题不存在")
                    for field, value in (await Topic.handle_params(payload)).items():
                        setattr(row, field, value)
                else:
                    payload.pop("id", None)
                    row = Topic(**await Topic.handle_params(payload))
                    session.add(row)
                await session.flush()
                await session.execute(delete(TopicGoods).where(TopicGoods.topic_id == row.id))
                session.add_all([
                    TopicGoods(topic_id=row.id, goods_id=goods_id, sort=index)
                    for index, goods_id in enumerate(goods_ids)
                ])
                return {"id": row.id}

    @staticmethod
    async def deleted(topic_id: int) -> int:
        if not await Topic.get(topic_id):
            raise ValueError("专题不存在")
        # 数据库同时级联物理删除专题商品关联，不删除商品本身。
        return await Topic.delete(topic_id, True)

    @staticmethod
    async def batch_deleted(ids: typing.List[int]) -> int:
        ids = list(dict.fromkeys(ids))
        if not ids:
            raise ValueError("请选择至少一条记录")
        async with async_session_factory() as session:
            async with session.begin():
                found = (await session.scalars(
                    select(Topic.id).where(Topic.id.in_(ids), Topic.enabled_flag.is_(True)).with_for_update()
                )).all()
                if len(found) != len(ids):
                    raise ValueError("部分专题不存在，请刷新后重试")
                result = await session.execute(delete(Topic).where(Topic.id.in_(ids)))
                return result.rowcount

    @staticmethod
    async def client_list(params: TopicQuery) -> typing.Dict[str, typing.Any]:
        data = await TopicService.list(params)
        fields = ("id", "title", "subtitle", "image", "price", "read_count", "read_count_text")
        data["rows"] = [{field: row.get(field) for field in fields} for row in data["rows"]]
        return data

    @staticmethod
    async def client_detail(topic_id: int) -> typing.Dict[str, typing.Any]:
        data = await TopicService.detail(topic_id)
        fields = ("id", "title", "subtitle", "image", "content", "price", "read_count", "read_count_text")
        result = {field: data.get(field) for field in fields}
        result["goods"] = [
            {key: product.get(key) for key in ("id", "name", "goods_sn", "image", "brief", "retail_price")}
            for product in data["goods"] if product.get("is_on_sale")
        ]
        return result

    @staticmethod
    async def export(params: TopicQuery) -> tuple[bytes, str]:
        rows = await Topic.get_all_by_query(params)
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "专题管理"
        sheet.append(EXPORT_HEADERS)
        center = Alignment(horizontal="center", vertical="center")
        for cell in sheet[1]:
            cell.fill = PatternFill("solid", fgColor="F2F5F8")
            cell.font = Font(bold=True, color="333333")
            cell.alignment = center
        for row in rows:
            TopicService._decorate(row)
            sheet.append([
                row.get("id"), row.get("title"), row.get("subtitle"), row.get("image"),
                row.get("price"), row.get("read_count"), row.get("creation_date"),
            ])
            for cell in sheet[sheet.max_row]:
                cell.alignment = center
                if isinstance(cell.value, str):
                    cell.data_type = "s"
        for index, width in enumerate([12, 26, 60, 45, 14, 16, 24], start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"专题列表_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
