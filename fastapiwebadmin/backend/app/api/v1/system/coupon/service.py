# -*- coding: utf-8 -*-
"""优惠券管理业务层"""

import typing
from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import delete, func, select
from sqlalchemy.orm import aliased

from app.api.v1.system.category.model import Category
from app.api.v1.system.coupon.model import Coupon, CouponCategory, CouponGoods, CouponUser
from app.api.v1.system.coupon.schema import CouponIn, CouponMineQuery, CouponQuery, CouponUserQuery
from app.api.v1.system.goods.model import Goods
from app.api.v1.system.member.model import Member
from app.database.sqlalchemy import async_session_factory
from app.shared.exceptions import AccessTokenFail
from app.utils.current_user import current_user

COUPON_TYPES = {0: "通用领券", 1: "注册赠券", 2: "兑换码"}
COUPON_STATUS = {0: "正常", 1: "已过期", 2: "已下架"}
GOODS_TYPES = {0: "全场通用", 1: "指定分类", 2: "指定商品"}
TIME_TYPES = {0: "领券相对天数", 1: "指定绝对时间"}
COUPON_USER_STATUS = {0: "未使用", 1: "已使用", 2: "已过期"}
EXPORT_HEADERS = ["优惠券ID", "优惠券名称", "介绍", "标签", "最低消费", "满减金额", "每人限领", "商品使用范围", "优惠券类型", "优惠券数量", "状态", "有效期"]


class CouponService:
    """优惠券定义与可用商品范围管理"""

    @staticmethod
    def _decorate(row: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        for field in ("min", "discount"):
            row[field] = float(row.get(field) or 0)
        min_text = format(row["min"], ".2f").rstrip("0").rstrip(".")
        discount_text = format(row["discount"], ".2f").rstrip("0").rstrip(".")
        row["min_text"] = f"满{min_text}元可用"
        row["discount_text"] = f"减免{discount_text}元"
        row["type_name"] = COUPON_TYPES.get(row.get("type"), "")
        row["goods_type_name"] = GOODS_TYPES.get(row.get("goods_type"), "")
        row["total_text"] = str(row.get("total")) if row.get("total") else "不限"
        row["time_type_name"] = TIME_TYPES.get(row.get("time_type"), "")
        effective_status = row.get("effective_status", row.get("status", 0))
        if effective_status == 0 and row.get("time_type") == 1 and row.get("end_time"):
            end = row["end_time"]
            end = end if isinstance(end, datetime) else datetime.fromisoformat(str(end))
            if end < datetime.now():
                effective_status = 1
        row["effective_status"] = effective_status
        row["status_name"] = COUPON_STATUS.get(effective_status, "")
        if row.get("time_type") == 0:
            row["time_text"] = f"领取后{row.get('days') or 0}天有效" if row.get("days") else "领取当日有效"
        else:
            row["time_text"] = f"{row.get('start_time') or ''} 至 {row.get('end_time') or ''}"
        return row

    # ---------------------------------------------------------------- 客户端（只读）
    @staticmethod
    async def client_list() -> typing.List[typing.Dict[str, typing.Any]]:
        rows = await Coupon.get_result(Coupon.client_stmt()) or []
        issued = {}
        if rows:
            async with async_session_factory() as session:
                counts = (await session.execute(
                    select(CouponUser.coupon_id, func.count(CouponUser.id))
                    .where(CouponUser.coupon_id.in_([row["id"] for row in rows]))
                    .group_by(CouponUser.coupon_id)
                )).all()
                issued = dict(counts)
        fields = (
            "id", "name", "description", "tag", "min", "discount",
            "time_type", "days", "start_time", "end_time", "total", "limit",
            "type", "goods_type",
        )
        result = []
        for row in rows:
            item = {key: row.get(key) for key in fields}
            item["min"] = float(item["min"] or 0)
            item["discount"] = float(item["discount"] or 0)
            item["min_text"] = "满{}元可用".format(
                format(item["min"], ".2f").rstrip("0").rstrip(".")
            )
            item["discount_text"] = "{}".format(
                format(item["discount"], ".2f").rstrip("0").rstrip(".")
            )
            if item["time_type"] == 0:
                item["time_text"] = (
                    "有效期：{}天".format(item["days"]) if item["days"] else "领取当日有效"
                )
            else:
                item["time_text"] = "有效期至 {}".format(item["end_time"] or "")
            item["goods_type_name"] = GOODS_TYPES.get(item["goods_type"], "")
            item["claimed_count"] = issued.get(row["id"], 0)
            item["remaining_total"] = max(0, item["total"] - item["claimed_count"]) if item["total"] else None
            item["can_claim"] = item["remaining_total"] is None or item["remaining_total"] > 0
            result.append(item)
        return result

    # ---------------------------------------------------------------- 会员领券与结算校验
    @staticmethod
    async def _member_id() -> int:
        user = await current_user()
        if not user or not user.get("member_id") or user.get("id"):
            raise AccessTokenFail()
        return int(user["member_id"])

    @staticmethod
    async def _member(session, member_id: int, lock: bool = False):
        stmt = select(Member).where(Member.id == member_id)
        if lock:
            stmt = stmt.with_for_update()
        member = await session.scalar(stmt)
        if not member or not member.enabled_flag or member.status != 1:
            raise AccessTokenFail()
        return member

    @staticmethod
    def _money(value) -> Decimal:
        return Decimal(str(value or 0)).quantize(Decimal("0.01"))

    @staticmethod
    def _claim_validity(coupon, now: datetime):
        if coupon.time_type == 1:
            if not coupon.start_time or not coupon.end_time:
                raise ValueError("优惠券有效期配置不完整")
            if coupon.start_time > now:
                raise ValueError("优惠券尚未开始领取")
            if coupon.end_time < now:
                raise ValueError("优惠券已过期")
            return coupon.start_time, coupon.end_time
        if coupon.days == 0:
            return now, now.replace(hour=23, minute=59, second=59, microsecond=0)
        try:
            return now, now + timedelta(days=coupon.days)
        except (OverflowError, ValueError):
            raise ValueError("优惠券有效天数超出可用范围")

    @staticmethod
    def _validity_window(user_coupon, coupon):
        """有效期窗口。

        - 绝对有效期券（time_type=1）：以**当前券定义**为准，后台改时间立即生效；
        - 相对天数券（time_type=0）：用领取时写入持券行的快照。
        """
        if coupon is not None and coupon.time_type == 1:
            return coupon.start_time, coupon.end_time
        return user_coupon.start_time, user_coupon.end_time

    @staticmethod
    def _effective_status(user_coupon, coupon, now: datetime) -> int:
        """0 未使用 / 1 已使用 / 2 已过期。

        已使用优先；券被删除、下架、手动置为过期，或有效期已过 → 已过期。
        """
        if user_coupon.status == 1:
            return 1
        if user_coupon.status == 2:
            return 2
        if coupon is None or not coupon.enabled_flag or coupon.status != 0:
            return 2
        _, end = CouponService._validity_window(user_coupon, coupon)
        if not end or end < now:
            return 2
        return 0

    @staticmethod
    def _client_user_row(user_coupon, coupon, now: datetime) -> typing.Dict[str, typing.Any]:
        start_time, end_time = CouponService._validity_window(user_coupon, coupon)
        effective_status = CouponService._effective_status(user_coupon, coupon, now)
        minimum = CouponService._money(coupon.min)
        discount = CouponService._money(coupon.discount)
        return {
            "id": user_coupon.id,
            "coupon_user_id": user_coupon.id,
            "coupon_id": coupon.id,
            "name": coupon.name,
            "description": coupon.description or "",
            "tag": coupon.tag or "",
            "min": float(minimum),
            "discount": float(discount),
            "min_text": f"满{minimum:.2f}元可用",
            "discount_text": f"减免{discount:.2f}元",
            "goods_type": coupon.goods_type,
            "goods_type_name": GOODS_TYPES.get(coupon.goods_type, ""),
            "type": coupon.type,
            "type_name": COUPON_TYPES.get(coupon.type, ""),
            "status": effective_status,
            "status_name": COUPON_USER_STATUS.get(effective_status, "未知"),
            "receive_time": user_coupon.receive_time.strftime("%Y-%m-%d %H:%M:%S"),
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S") if start_time else None,
            "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S") if end_time else None,
            "time_text": "{} 至 {}".format(
                start_time.strftime("%Y-%m-%d %H:%M:%S") if start_time else "未设置",
                end_time.strftime("%Y-%m-%d %H:%M:%S") if end_time else "未设置",
            ),
            "order_id": user_coupon.order_id,
            "use_time": user_coupon.use_time.strftime("%Y-%m-%d %H:%M:%S") if user_coupon.use_time else None,
        }

    @staticmethod
    async def claim(coupon_id: int) -> typing.Dict[str, typing.Any]:
        member_id = await CouponService._member_id()
        async with async_session_factory() as session, session.begin():
            await CouponService._member(session, member_id, lock=True)
            coupon = await session.scalar(select(Coupon).where(Coupon.id == coupon_id).with_for_update())
            if not coupon or not coupon.enabled_flag:
                raise ValueError("优惠券不存在或已删除")
            if coupon.type != 0:
                raise ValueError("该优惠券不支持首页领取")
            if coupon.status != 0:
                raise ValueError("优惠券已过期或已下架")
            now = datetime.now().replace(microsecond=0)
            start, end = CouponService._claim_validity(coupon, now)
            if coupon.total < 0 or coupon.limit < 1:
                raise ValueError("优惠券领取规则异常")
            # 已使用、已过期以及逻辑隐藏的历史领取也占发行量和每人限领。
            issued = await session.scalar(select(func.count(CouponUser.id)).where(CouponUser.coupon_id == coupon.id))
            if coupon.total and issued >= coupon.total:
                raise ValueError("优惠券已领完")
            own_count = await session.scalar(select(func.count(CouponUser.id)).where(
                CouponUser.coupon_id == coupon.id, CouponUser.user_id == member_id
            ))
            if own_count >= coupon.limit:
                raise ValueError("已达到该优惠券的每人领取上限")
            row = CouponUser(coupon_id=coupon.id, user_id=member_id, receive_time=now,
                             start_time=start, end_time=end, status=0)
            session.add(row)
            await session.flush()
            result = CouponService._client_user_row(row, coupon, now)
            result["remaining_total"] = max(0, coupon.total - issued - 1) if coupon.total else None
            result["remaining_for_member"] = max(0, coupon.limit - own_count - 1)
            return result

    @staticmethod
    async def my_list(params: CouponMineQuery) -> typing.Dict[str, typing.Any]:
        member_id = await CouponService._member_id()
        async with async_session_factory() as session:
            await CouponService._member(session, member_id)
            pairs = (await session.execute(
                select(CouponUser, Coupon).join(Coupon, Coupon.id == CouponUser.coupon_id)
                .where(CouponUser.user_id == member_id, CouponUser.enabled_flag.is_(True))
                .order_by(CouponUser.receive_time.desc(), CouponUser.id.desc())
            )).all()
            rows = [CouponService._client_user_row(row, coupon, datetime.now()) for row, coupon in pairs]
            if params.status is not None:
                rows = [row for row in rows if row["status"] == params.status]
            return {"rows": rows, "rowTotal": len(rows)}

    @staticmethod
    def _use_reason(user_coupon, coupon, member_id: int, now: datetime) -> str:
        if not user_coupon or not user_coupon.enabled_flag or user_coupon.user_id != member_id:
            return "优惠券不存在或不属于当前用户"
        if user_coupon.status == 1:
            return "优惠券已使用"
        if user_coupon.status != 0:
            return "优惠券已过期"
        if not coupon or not coupon.enabled_flag:
            return "优惠券已删除"
        if coupon.status != 0:
            return "优惠券已过期或已下架"
        # 与展示保持同一套有效期口径：绝对有效期券跟着后台当前配置走
        start, end = CouponService._validity_window(user_coupon, coupon)
        if not start or not end:
            return "优惠券有效期信息不完整"
        if end < now:
            return "优惠券已过期"
        if start > now:
            return "优惠券尚未到使用时间"
        return ""

    @staticmethod
    async def _scope_maps(session, coupon_ids: typing.List[int], lock: bool = False):
        categories = (await session.execute(select(Category.id, Category.parent_id, Category.level)
                                            .where(Category.enabled_flag.is_(True)))).all()
        roots = {row.id for row in categories if row.level == 1 and row.parent_id == 0}
        parents = {row.id: row.parent_id for row in categories
                   if row.id in roots or row.level == 2 and row.parent_id in roots}
        category_targets, goods_targets = {}, {}
        if coupon_ids:
            category_stmt = select(CouponCategory.coupon_id, CouponCategory.category_id).where(
                CouponCategory.coupon_id.in_(coupon_ids), CouponCategory.enabled_flag.is_(True)
            )
            goods_stmt = select(CouponGoods.coupon_id, CouponGoods.goods_id).where(
                CouponGoods.coupon_id.in_(coupon_ids), CouponGoods.enabled_flag.is_(True)
            )
            if lock:
                # 券定义已锁定后读取其当前范围，避免与旧 MVCC 快照混用。
                category_stmt = category_stmt.with_for_update()
                goods_stmt = goods_stmt.with_for_update()
            for coupon_id, category_id in (await session.execute(category_stmt)).all():
                if category_id in parents:
                    category_targets.setdefault(coupon_id, set()).add(category_id)
            for coupon_id, goods_id in (await session.execute(goods_stmt)).all():
                goods_targets.setdefault(coupon_id, set()).add(goods_id)
        return parents, category_targets, goods_targets

    @staticmethod
    def _order_discount(user_coupon, coupon, member_id: int, lines, now: datetime, scopes):
        reason = CouponService._use_reason(user_coupon, coupon, member_id, now)
        if reason:
            return Decimal("0.00"), Decimal("0.00"), reason
        parents, category_targets, goods_targets = scopes
        eligible = Decimal("0.00")
        for line in lines:
            category_id = line.get("category_id")
            allowed = coupon.goods_type == 0
            if coupon.goods_type == 1:
                targets = category_targets.get(coupon.id, set())
                allowed = category_id in parents and (category_id in targets or parents[category_id] in targets)
            elif coupon.goods_type == 2:
                allowed = line.get("goods_id") in goods_targets.get(coupon.id, set())
            if allowed:
                eligible += CouponService._money(line["price"]) * int(line["quantity"])
        if eligible <= 0:
            return eligible, Decimal("0.00"), "订单中没有符合优惠券使用范围的商品"
        if eligible < CouponService._money(coupon.min):
            return eligible, Decimal("0.00"), "适用商品金额未达到满减门槛"
        discount = min(CouponService._money(coupon.discount), eligible)
        if discount <= 0:
            return eligible, Decimal("0.00"), "该优惠券暂无可抵扣金额"
        return eligible, discount, ""

    @staticmethod
    async def order_coupons(session, member_id: int, lines, now: datetime = None) -> typing.List[typing.Dict[str, typing.Any]]:
        """供订单预览读取本人持券，不自行提交或修改订单事务。"""
        now = now or datetime.now()
        pairs = (await session.execute(
            select(CouponUser, Coupon).join(Coupon, Coupon.id == CouponUser.coupon_id)
            .where(CouponUser.user_id == member_id, CouponUser.enabled_flag.is_(True), CouponUser.status != 1)
            .order_by(CouponUser.receive_time.desc(), CouponUser.id.desc())
        )).all()
        scopes = await CouponService._scope_maps(session, [coupon.id for _, coupon in pairs])
        rows = []
        for user_coupon, coupon in pairs:
            eligible, discount, reason = CouponService._order_discount(user_coupon, coupon, member_id, lines, now, scopes)
            row = CouponService._client_user_row(user_coupon, coupon, now)
            row.update({"available": not bool(reason), "reason": reason,
                        "eligible_amount": float(eligible), "eligible_amount_text": format(eligible, ".2f"),
                        "discount_amount": float(discount), "discount_amount_text": format(discount, ".2f")})
            rows.append(row)
        return rows

    @staticmethod
    async def validate_order_coupon(session, member_id: int, coupon_user_id: int, lines,
                                    now: datetime = None, lock: bool = False):
        """在调用方订单事务内重新校验，返回持券行及真实可抵扣金额。"""
        now = now or datetime.now()
        # 固定先锁券定义再锁持券，和领取/后台修改保持一致。
        coupon_id = await session.scalar(select(CouponUser.coupon_id).where(
            CouponUser.id == coupon_user_id, CouponUser.user_id == member_id, CouponUser.enabled_flag.is_(True)
        ))
        if not coupon_id:
            raise ValueError("优惠券不存在或不属于当前用户")
        coupon_stmt = select(Coupon).where(Coupon.id == coupon_id).execution_options(populate_existing=True)
        user_stmt = select(CouponUser).where(CouponUser.id == coupon_user_id, CouponUser.user_id == member_id).execution_options(populate_existing=True)
        if lock:
            coupon_stmt = coupon_stmt.with_for_update()
            user_stmt = user_stmt.with_for_update()
        coupon = await session.scalar(coupon_stmt)
        user_coupon = await session.scalar(user_stmt)
        scopes = await CouponService._scope_maps(session, [coupon_id], lock=lock)
        _, discount, reason = CouponService._order_discount(user_coupon, coupon, member_id, lines, now, scopes)
        if reason:
            raise ValueError(reason)
        return user_coupon, discount

    @staticmethod
    async def list(params: CouponQuery) -> typing.Dict[str, typing.Any]:
        data = await Coupon.get_list(params)
        for row in data.get("rows", []):
            CouponService._decorate(row)
        return data

    @staticmethod
    async def user_list(params: CouponUserQuery) -> typing.Dict[str, typing.Any]:
        """后台详情页只读取当前优惠券的领取记录，不产生模拟领取数据。"""
        if not await Coupon.get(params.coupon_id):
            raise ValueError("优惠券不存在")
        data = await CouponUser.get_list(params)
        for row in data.get("rows", []):
            row["status_name"] = COUPON_USER_STATUS.get(row.get("effective_status", row.get("status")), "")
        return data

    @staticmethod
    async def detail(coupon_id: int) -> typing.Dict[str, typing.Any]:
        row = await Coupon.get(coupon_id, to_dict=True)
        if not row:
            raise ValueError("优惠券不存在")
        parent = aliased(Category)
        categories = await CouponCategory.get_result(
            select(CouponCategory.category_id.label("id"), Category.name, parent.name.label("parent_name"))
            .outerjoin(Category, (Category.id == CouponCategory.category_id) & Category.enabled_flag.is_(True))
            .outerjoin(parent, (parent.id == Category.parent_id) & parent.enabled_flag.is_(True))
            .where(CouponCategory.coupon_id == coupon_id)
            .order_by(CouponCategory.id.asc())
        ) or []
        for category in categories:
            category["name"] = category.get("name") or f"已删除分类（{category['id']}）"
            category["path_name"] = (
                f"{category['parent_name']}>{category['name']}" if category.get("parent_name") else category["name"]
            )
        goods = await CouponGoods.get_result(
            select(CouponGoods.goods_id.label("id"), Goods.name, Goods.goods_sn)
            .outerjoin(Goods, (Goods.id == CouponGoods.goods_id) & Goods.enabled_flag.is_(True))
            .where(CouponGoods.coupon_id == coupon_id)
            .order_by(CouponGoods.id.asc())
        ) or []
        for product in goods:
            product["name"] = product.get("name") or f"已删除商品（{product['id']}）"
        row["categories"] = categories
        row["goods"] = goods
        row["category_ids"] = [category["id"] for category in categories]
        row["goods_ids"] = [product["id"] for product in goods]
        return CouponService._decorate(row)

    @staticmethod
    async def save_or_update(params: CouponIn) -> typing.Dict[str, typing.Any]:
        payload = params.model_dump(exclude_none=False)
        payload["name"] = (payload["name"] or "").strip()
        if not payload["name"]:
            raise ValueError("优惠券名称不能为空")
        for field in ("description", "tag"):
            payload[field] = (payload[field] or "").strip()
        if params.time_type == 0:
            payload["start_time"] = payload["end_time"] = None
        else:
            if not params.start_time or not params.end_time:
                raise ValueError("请选择完整的优惠券起止时间")
            if params.start_time.tzinfo or params.end_time.tzinfo:
                raise ValueError("日期时间请使用本地时间，不要携带时区")
            if params.start_time >= params.end_time:
                raise ValueError("结束时间必须晚于开始时间")
            payload["days"] = 0
        category_ids = list(dict.fromkeys(payload.pop("category_ids"))) if params.goods_type == 1 else []
        goods_ids = list(dict.fromkeys(payload.pop("goods_ids"))) if params.goods_type == 2 else []
        payload.pop("category_ids", None)
        payload.pop("goods_ids", None)
        if params.goods_type == 1 and not category_ids:
            raise ValueError("请先添加商品分类")
        if params.goods_type == 2 and not goods_ids:
            raise ValueError("请先添加商品")

        async with async_session_factory() as session:
            async with session.begin():
                for ids, model, label in ((category_ids, Category, "分类"), (goods_ids, Goods, "商品")):
                    if ids:
                        found = (await session.scalars(
                            select(model.id).where(model.id.in_(ids), model.enabled_flag.is_(True)).with_for_update()
                        )).all()
                        if len(found) != len(ids):
                            raise ValueError(f"选择的{label}不存在，请刷新后重试")
                if params.id:
                    row = await session.get(Coupon, params.id, with_for_update=True)
                    if not row or not row.enabled_flag:
                        raise ValueError("优惠券不存在")
                    for field, value in (await Coupon.handle_params(payload)).items():
                        setattr(row, field, value)
                else:
                    payload.pop("id", None)
                    row = Coupon(**await Coupon.handle_params(payload))
                    session.add(row)
                await session.flush()
                # 主记录与使用范围在同一事务里替换；切换范围时清除旧关联。
                await session.execute(delete(CouponCategory).where(CouponCategory.coupon_id == row.id))
                await session.execute(delete(CouponGoods).where(CouponGoods.coupon_id == row.id))
                session.add_all([CouponCategory(coupon_id=row.id, category_id=cid) for cid in category_ids])
                session.add_all([CouponGoods(coupon_id=row.id, goods_id=gid) for gid in goods_ids])
                return {"id": row.id}

    @staticmethod
    async def deleted(coupon_id: int) -> int:
        if not await Coupon.get(coupon_id):
            raise ValueError("优惠券不存在")
        # 范围与会员领券记录通过 ON DELETE CASCADE 一并物理删除。
        return await Coupon.delete(coupon_id, True)

    @staticmethod
    async def matches_goods(coupon_id: int, goods_id: int) -> bool:
        """供后续结算接入：仅判断商品范围，不替代领券、有效期和订单金额校验。"""
        coupon = await Coupon.get(coupon_id, to_dict=True)
        goods = await Goods.get(goods_id, to_dict=True)
        if not coupon or not goods:
            return False
        if coupon["goods_type"] == 0:
            return True
        if coupon["goods_type"] == 2:
            return bool(await CouponGoods.get_result(
                select(CouponGoods.id).where(CouponGoods.coupon_id == coupon_id, CouponGoods.goods_id == goods_id),
                first=True,
            ))
        category_id = goods.get("category_id")
        ids = []
        while category_id and category_id not in ids:
            category = await Category.get(category_id, to_dict=True)
            if not category:
                break
            ids.append(category_id)
            category_id = category.get("parent_id")
        if not ids:
            return False
        return bool(await CouponCategory.get_result(
            select(CouponCategory.id).where(CouponCategory.coupon_id == coupon_id, CouponCategory.category_id.in_(ids)),
            first=True,
        ))

    @staticmethod
    async def export(params: CouponQuery) -> tuple[bytes, str]:
        rows = await Coupon.get_all_by_query(params)
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "优惠券管理"
        sheet.append(EXPORT_HEADERS)
        center = Alignment(horizontal="center", vertical="center")
        for cell in sheet[1]:
            cell.fill = PatternFill("solid", fgColor="F2F5F8")
            cell.font = Font(bold=True, color="333333")
            cell.alignment = center
        for row in rows:
            CouponService._decorate(row)
            sheet.append([
                row.get("id"), row.get("name"), row.get("description"), row.get("tag"), row.get("min"),
                row.get("discount"), row.get("limit"), row.get("goods_type_name"), row.get("type_name"),
                row.get("total_text"), row.get("status_name"), row.get("time_text"),
            ])
            for cell in sheet[sheet.max_row]:
                cell.alignment = center
                if isinstance(cell.value, str):
                    cell.data_type = "s"
        for index, width in enumerate([12, 24, 36, 22, 14, 14, 14, 18, 18, 16, 14, 45], start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue(), f"优惠券列表_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
