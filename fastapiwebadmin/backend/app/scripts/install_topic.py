# -*- coding: utf-8 -*-
"""幂等安装专题管理菜单并初始化示例：python -m app.scripts.install_topic。"""

import asyncio
import json
from decimal import Decimal
from html import escape
from io import BytesIO
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import Headers, UploadFile

from app.api.v1.common.file.model import FileInfo
from app.api.v1.common.file.service import FileService
from app.api.v1.system.goods.model import Goods
from app.api.v1.system.menu.model import Menu
from app.api.v1.system.roles.model import RoleMenu, Roles
from app.api.v1.system.topic.model import Topic, TopicGoods
from app.config.setting import settings
from app.database.database import create_tables
from app.database.sqlalchemy import async_session_factory, engine


def _local_image_exists(url: str) -> bool:
    """复用当前服务可访问的本地封面，避免演示数据引用失效图片。"""
    prefix = settings.UPLOAD_URL_PREFIX.rstrip("/") + "/"
    if not url.startswith(prefix):
        return False
    root = Path(settings.upload_local_dir).resolve()
    path = (root / url[len(prefix):]).resolve()
    return path.is_relative_to(root) and path.is_file()


async def _demo_cover(session: AsyncSession, index: int, title: str) -> str:
    """没有可复用商品图片时，生成原创 SVG 并交给统一文件服务保存。"""
    filename = ["topic-demo-home.svg", "topic-demo-style.svg", "topic-demo-travel.svg"][index]
    existing = await session.scalar(
        select(FileInfo.file_url)
        .where(
            FileInfo.enabled_flag.is_(True),
            FileInfo.original_name == filename,
            FileInfo.file_path.like("topics/demo/%"),
        )
        .order_by(FileInfo.creation_date.desc())
        .limit(1)
    )
    if existing and _local_image_exists(existing):
        return existing
    background, accent, label = [
        ("#eef7f2", "#4b8267", "让生活多一点舒适"),
        ("#f8f1ec", "#aa795d", "找到适合自己的风格"),
        ("#eef3fa", "#567ba6", "轻装出发从容收纳"),
    ][index]
    symbol = [
        '<path d="M678 274 L758 210 L838 274 V378 H678 Z"/><path d="M735 378 V307 H781 V378"/>',
        '<path d="M712 224 L742 210 Q758 234 774 210 L804 224 L846 282 L811 307 L798 290 V378 H718 V290 L705 307 L670 282 Z"/>',
        '<rect x="688" y="255" width="140" height="123" rx="20"/><path d="M728 255 V224 H788 V255 M712 278 V356 M804 278 V356"/>',
    ][index]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540">
<rect width="960" height="540" rx="28" fill="{background}"/>
<circle cx="785" cy="100" r="180" fill="{accent}" opacity="0.08"/>
<circle cx="115" cy="525" r="150" fill="{accent}" opacity="0.08"/>
<rect x="52" y="56" width="856" height="428" rx="24" fill="white" opacity="0.72"/>
<text x="94" y="222" fill="{accent}" font-family="Microsoft YaHei, sans-serif" font-size="42" font-weight="bold">{escape(title)}</text>
<text x="98" y="274" fill="#6e7b77" font-family="Microsoft YaHei, sans-serif" font-size="24">{label}</text>
<rect x="98" y="316" width="68" height="5" rx="2.5" fill="{accent}"/>
<g fill="none" stroke="{accent}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round">{symbol}</g>
</svg>'''
    file = UploadFile(
        file=BytesIO(svg.encode("utf-8")),
        filename=filename,
        headers=Headers({"content-type": "image/svg+xml"}),
    )
    try:
        result = await FileService.upload(file, "topics/demo")
    finally:
        await file.close()
    return result["url"]


async def _seed_topics(session: AsyncSession) -> int:
    """仅空表时预置三条原创文章，关联已有商品，不修改用户专题。"""
    count = await session.scalar(select(func.count()).select_from(Topic))
    if count:
        return 0
    goods = (await session.scalars(
        select(Goods).where(Goods.enabled_flag.is_(True)).order_by(Goods.id.asc()).limit(6)
    )).all()
    candidate_images = (await session.scalars(
        select(Goods.image)
        .where(Goods.enabled_flag.is_(True), Goods.image.is_not(None), Goods.image != "")
        .distinct()
        .limit(100)
    )).all()
    covers = [url for url in candidate_images if _local_image_exists(url)]
    examples = [
        {
            "title": "居家好物指南",
            "subtitle": "从常用物件开始，整理一个舒适有序的家",
            "price": Decimal("29.90"),
            "read_count": 42500,
            "paragraphs": [
                "家里的舒适感，往往来自每天都会用到的小物件。选购之前，先留意自己的起居习惯：哪些东西需要随手拿到，哪些角落总是容易堆满。",
                "把常用物品安排在顺手的位置，为它们保留固定的收纳空间，比一次买齐整套用品更实用。材质耐用、清洁方便、尺寸合适，是日常挑选时可以优先考虑的三个条件。",
                "本专题整理了一组居家生活的选购思路。可以从一两件真正需要的用品开始，让改变慢慢融入日常，而不是给家里增加新的负担。",
            ],
        },
        {
            "title": "日常穿搭灵感",
            "subtitle": "用简洁配色与舒适细节，找到适合自己的风格",
            "price": Decimal("59.90"),
            "read_count": 12800,
            "paragraphs": [
                "日常穿搭可以从舒服开始。先挑出衣橱里最常穿、最适合自己的几件单品，再围绕它们搭配，比不断追逐新的款式更容易建立稳定的个人风格。",
                "同一套基础搭配，可以通过鞋子、包袋和一件外搭改变感觉。控制整体颜色的数量，留意衣物之间的比例，通常就能让出门前的选择轻松许多。",
                "专题中的商品用于展示不同的搭配方向。选购时仍应结合实际尺码、使用场景和已有衣物，给自己保留灵活组合的空间。",
            ],
        },
        {
            "title": "出行收纳清单",
            "subtitle": "按使用场景分区打包，让每一次出发更从容",
            "price": Decimal("15.00"),
            "read_count": 7800,
            "paragraphs": [
                "打包行李之前，先按行程天数列一份简短清单。把衣物、洗护、随身文件和电子配件分开考虑，可以减少重复携带，也更容易发现遗漏的必需品。",
                "收纳不必追求装得最多，而应让取用更方便。常用小物放在容易打开的位置，需要保持干燥或单独保护的物品分区放置，返程时也能更快归整。",
                "不论是周末短途还是日常通勤，都可以从这份清单中挑选适合自己的部分。保留一点空余空间，给旅途中的新发现留出位置。",
            ],
        },
    ]
    for index, values in enumerate(examples):
        title = values["title"]
        image = covers[index % len(covers)] if covers else await _demo_cover(session, index, title)
        content = f"<h2>{escape(title)}</h2>" + "".join(f"<p>{escape(text)}</p>" for text in values["paragraphs"])
        topic = Topic(
            title=title,
            subtitle=values["subtitle"],
            image=image,
            content=content,
            price=values["price"],
            read_count=values["read_count"],
        )
        session.add(topic)
        await session.flush()
        related = goods[index * 2:index * 2 + 2] or goods[:2]
        session.add_all([
            TopicGoods(topic_id=topic.id, goods_id=product.id, sort=sort)
            for sort, product in enumerate(related)
        ])
    return len(examples)


async def install() -> None:
    """创建缺失表、安装专题菜单权限，并在空表中预置三条示例。"""
    await create_tables()
    json_path = Path(__file__).parent / "data" / "sys_menu.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    root = next((item for item in data if item["path"] == "/promotion"), None)
    if root is None:
        raise ValueError("初始化数据中缺少推广管理菜单")

    topic_paths = ["/promotion/topic", "/promotion/topicCreate", "/promotion/topicEdit"]
    children = [item for item in root.get("children", []) if item["path"] in topic_paths]
    if len(children) != len(topic_paths):
        raise ValueError("初始化数据中缺少专题管理、专题创建或专题编辑菜单")

    # 仅同步推广管理根节点和专题相关页面，不改动广告、优惠券等其他模块。
    root = {**root, "children": children}
    async with async_session_factory() as session:
        async with session.begin():
            menu_ids = []

            async def upsert(item, parent_id=0):
                values = {key: value for key, value in item.items() if key != "children"}
                values.setdefault("isLink", 0)
                values.setdefault("isHide", 0)
                values.setdefault("isKeepAlive", 1)
                values.setdefault("isAffix", 0)
                values.setdefault("isIframe", 0)
                condition = (
                    Menu.roles == values["roles"]
                    if values.get("roles")
                    else Menu.path == values["path"]
                )
                row = await session.scalar(select(Menu).where(condition))
                if row is None:
                    row = Menu(**values, parent_id=parent_id)
                    session.add(row)
                else:
                    for key, value in values.items():
                        setattr(row, key, value)
                    row.parent_id = parent_id
                    row.enabled_flag = True
                await session.flush()
                menu_ids.append(row.id)
                for child in item.get("children", []):
                    await upsert(child, row.id)

            await upsert(root)
            role_id = await session.scalar(
                select(Roles.id).where(Roles.name == "管理员", Roles.enabled_flag.is_(True))
            )
            if role_id:
                for menu_id in menu_ids:
                    if not await session.get(RoleMenu, (role_id, menu_id)):
                        session.add(RoleMenu(role_id=role_id, menu_id=menu_id))
            seeded = await _seed_topics(session)
    print(f"专题表和菜单安装完成，本次新增 {seeded} 条示例专题")


if __name__ == "__main__":
    async def main() -> None:
        try:
            await install()
        finally:
            await engine.dispose()

    asyncio.run(main())
