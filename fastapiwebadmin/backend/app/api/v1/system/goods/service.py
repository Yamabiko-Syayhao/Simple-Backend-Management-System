"""商品业务层；关联写入使用独立事务，失败整体回滚。"""
from datetime import datetime
from io import BytesIO
from sqlalchemy import select, delete
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from app.database.sqlalchemy import async_session_factory
from app.api.v1.system.goods.model import Goods, GoodsSpecification, GoodsProduct, GoodsAttribute
from app.api.v1.system.brand.model import Brand
from app.api.v1.system.category.model import Category


class GoodsService:
    @staticmethod
    def _decorate(row):
        for key in ("market_price", "retail_price", "price"):
            if key in row:
                row[key] = float(row[key] or 0)
        for key, yes, no in (("is_new", "新品", "非新品"), ("is_hot", "热品", "非热品"), ("is_on_sale", "在售", "未售")):
            if key in row:
                row[key + "_text"] = yes if row[key] else no
        return row

    @staticmethod
    async def list(params):
        data = await Goods.get_list(params)
        data["rows"] = [GoodsService._decorate(row) for row in data["rows"]]
        return data

    @staticmethod
    async def detail(goods_id):
        row = await Goods.get(goods_id, to_dict=True)
        if not row:
            raise ValueError("商品不存在")
        for key, model in (("specifications", GoodsSpecification), ("products", GoodsProduct), ("attributes", GoodsAttribute)):
            rows = await model.get_result(select(model.get_table_columns()).where(model.goods_id == goods_id).order_by(model.id))
            row[key] = [GoodsService._decorate(child) for child in (rows or [])]
        return GoodsService._decorate(row)

    # ---------------------------------------------------------------- 客户端（只读）
    CLIENT_FIELDS = (
        "id", "name", "goods_sn", "image", "brief", "retail_price",
        "market_price", "unit", "is_new", "is_hot", "brand_id", "category_id",
    )

    @staticmethod
    async def client_list(params):
        data = await Goods.pagination(Goods.client_stmt(params))
        data["rows"] = [
            GoodsService._decorate({key: row.get(key) for key in GoodsService.CLIENT_FIELDS})
            for row in data["rows"]
        ]
        return data

    @staticmethod
    async def client_detail(goods_id):
        row = await GoodsService.detail(goods_id)
        result = {key: row.get(key) for key in GoodsService.CLIENT_FIELDS}
        result["is_on_sale"] = bool(row.get("is_on_sale"))
        result["gallery"] = row.get("gallery") or []
        result["detail"] = row.get("detail") or ""
        result["attributes"] = [
            {"name": item.get("name"), "value": item.get("value")}
            for item in (row.get("attributes") or [])
        ]
        result["specifications"] = [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "value": item.get("value"),
                "image": item.get("image"),
            }
            for item in (row.get("specifications") or [])
            if item.get("enabled_flag", True)
        ]
        # 购买规格必须使用库存行的真实 ID，不能用规格表 ID 代替。
        result["products"] = [
            {
                "id": item.get("id"),
                "specification": item.get("specification") or "标准",
                "price": float(item.get("price") or 0),
                "quantity": max(0, int(item.get("quantity") or 0)),
                "image": item.get("image") or row.get("image") or "",
            }
            for item in (row.get("products") or [])
            if item.get("enabled_flag", True)
        ]
        result["stock"] = sum(item["quantity"] for item in result["products"])
        result["cart_available"] = result["is_on_sale"] and result["stock"] > 0
        return result

    @staticmethod
    async def save_or_update(params):
        payload = params.model_dump(exclude_none=False)
        payload["name"] = payload["name"].strip()
        payload["goods_sn"] = (payload["goods_sn"] or "").strip() or None
        if not payload["name"]:
            raise ValueError("商品名称不能为空")
        async with async_session_factory() as session, session.begin():
            for field, model in (("category_id", Category), ("brand_id", Brand)):
                if payload[field] and not await session.get(model, payload[field]):
                    raise ValueError("所选类目或品牌不存在")
            if payload["goods_sn"]:
                existing = await session.scalar(select(Goods.id).where(Goods.goods_sn == payload["goods_sn"]))
                if existing and existing != params.id:
                    raise ValueError("商品编号已存在")
            if params.id:
                row = await session.get(Goods, params.id, with_for_update=True)
                if not row:
                    raise ValueError("商品不存在")
                # 当前价格由库存维护，基本信息保存不能覆盖已更新库存价格。
                payload.pop("retail_price")
                for key, value in (await Goods.handle_params(payload)).items():
                    setattr(row, key, value)
            else:
                payload.pop("id")
                # 首次保存仅创建未售商品，配置子项后再显式上架。
                payload["is_on_sale"] = False
                row = Goods(**await Goods.handle_params(payload))
                session.add(row)
                await session.flush()
                session.add(GoodsSpecification(goods_id=row.id, name="规格", value="标准", image=""))
                session.add(GoodsProduct(goods_id=row.id, specification="标准", price=row.retail_price, quantity=0, image=row.image))
            await session.flush()
            return {"id": row.id}

    @staticmethod
    async def deleted(ids):
        ids = list(set(ids))
        if not ids or any(i <= 0 for i in ids):
            raise ValueError("请选择商品")
        async with async_session_factory() as session, session.begin():
            found = (await session.scalars(select(Goods.id).where(Goods.id.in_(ids)).with_for_update())).all()
            if len(found) != len(ids):
                raise ValueError("部分商品不存在，请刷新后重试")
            for model in (GoodsAttribute, GoodsProduct, GoodsSpecification):
                await session.execute(delete(model).where(model.goods_id.in_(ids)))
            await session.execute(delete(Goods).where(Goods.id.in_(ids)))
        return len(ids)

    @staticmethod
    async def save_child(kind, params):
        model = {"specification": GoodsSpecification, "product": GoodsProduct, "attribute": GoodsAttribute}[kind]
        async with async_session_factory() as session, session.begin():
            goods = await session.get(Goods, params.goods_id, with_for_update=True)
            if not goods:
                raise ValueError("商品不存在")
            row = await session.get(model, params.id) if params.id else None
            if params.id and (not row or row.goods_id != params.goods_id):
                raise ValueError("记录不存在或不属于该商品")
            if kind == "product" and not row:
                raise ValueError("库存记录不存在")
            if kind == "product":
                row.price, row.quantity, row.image = params.price, params.quantity, params.image
                goods.retail_price = params.price
            else:
                if not params.name.strip() or not params.value.strip():
                    raise ValueError("名称和值不能为空")
                if kind == "specification" and (len(params.name) > 64 or len(params.value) > 128):
                    raise ValueError("规格名称或值过长")
                if row is None:
                    row = model(goods_id=params.goods_id)
                    session.add(row)
                row.name, row.value = params.name.strip(), params.value.strip()
                if kind == "specification":
                    row.image = params.image
                    products = (await session.scalars(select(GoodsProduct).where(GoodsProduct.goods_id == goods.id))).all()
                    for product in products:
                        product.specification = row.value
            await session.flush()
            return {"id": row.id}

    @staticmethod
    async def delete_attribute(params):
        async with async_session_factory() as session, session.begin():
            row = await session.get(GoodsAttribute, params.id)
            if not row or row.goods_id != params.goods_id:
                raise ValueError("商品参数不存在")
            await session.delete(row)

    @staticmethod
    async def export(params):
        rows = await Goods.get_result(Goods._build_stmt(params))
        book = Workbook()
        sheet = book.active
        sheet.title = "商品列表"
        sheet.append(["商品ID", "名称", "商品编号", "市场售价", "当前价格", "是否新品", "是否热品", "是否在售"])
        for cell in sheet[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="F2F5F8")
        for row in (rows or []):
            GoodsService._decorate(row)
            values = [row.get(k) for k in ("id", "name", "goods_sn", "market_price", "retail_price", "is_new_text", "is_hot_text", "is_on_sale_text")]
            sheet.append(values)
            for cell in sheet[sheet.max_row]:
                if isinstance(cell.value, str):
                    cell.data_type = "s"
        for col in "ABCDEFGH":
            sheet.column_dimensions[col].width = 22
        out = BytesIO()
        book.save(out)
        return out.getvalue(), f"商品列表_{datetime.now():%Y%m%d%H%M%S}.xlsx"

