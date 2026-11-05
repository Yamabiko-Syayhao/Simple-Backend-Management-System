"""商品及其规格、库存、参数数据层。"""
from sqlalchemy import Column, String, Text, Numeric, Integer, BigInteger, Boolean, JSON, ForeignKey, cast, or_, select
from app.api.v1.system.category.model import Category
from app.models.base import Base


class Goods(Base):
    __tablename__ = "mal_goods"
    name = Column(String(128), nullable=False, index=True)
    goods_sn = Column(String(64), unique=True, nullable=True)
    market_price = Column(Numeric(12, 2), nullable=False, default=0)
    retail_price = Column(Numeric(12, 2), nullable=False, default=0)
    is_new = Column(Boolean, default=False, nullable=False)
    is_hot = Column(Boolean, default=False, nullable=False)
    is_on_sale = Column(Boolean, default=False, nullable=False)
    image = Column(Text)
    share_image = Column(Text)
    gallery = Column(JSON)
    unit = Column(String(32), default="件")
    keywords = Column(JSON)
    category_id = Column(BigInteger, default=0)
    brand_id = Column(BigInteger, default=0)
    brief = Column(String(500))
    detail = Column(Text)

    @classmethod
    def _build_stmt(cls, params):
        q = [cls.enabled_flag.is_(True)]
        if params.goods_id:
            q.append(cls.id == params.goods_id)
        if params.goods_sn:
            q.append(cls.goods_sn.like(f"%{params.goods_sn}%"))
        if params.name:
            q.append(cls.name.like(f"%{params.name}%"))
        return select(cls.get_table_columns()).where(*q).order_by(cls.id.asc() if params.sort_order == "asc" else cls.id.desc())

    @classmethod
    async def get_list(cls, params):
        return await cls.pagination(cls._build_stmt(params))

    @classmethod
    def client_stmt(cls, params):
        """客户端列表 / 搜索：关键字同时匹配商品名称与关键字字段"""
        q = [cls.enabled_flag.is_(True)]
        keyword = (getattr(params, "keyword", None) or "").strip()
        if keyword:
            q.append(
                or_(
                    cls.name.like("%{}%".format(keyword)),
                    cast(cls.keywords, String).like("%{}%".format(keyword)),
                )
            )
        if getattr(params, "brand_id", None):
            q.append(cls.brand_id == params.brand_id)
        category_id = getattr(params, "category_id", None)
        if category_id is not None:
            q.append(cls.category_id.in_(Category.client_scope_ids(category_id)))

        scene = getattr(params, "scene", None) or "default"
        if scene == "new":
            order = (cls.creation_date.desc(), cls.id.desc())
        elif scene == "hot":
            order = (cls.is_hot.desc(), cls.id.desc())
        else:
            order = (cls.id.desc(),)
        return select(cls.get_table_columns()).where(*q).order_by(*order)


class GoodsSpecification(Base):
    __tablename__ = "mal_goods_specification"
    goods_id = Column(BigInteger, ForeignKey("mal_goods.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(64), nullable=False, default="规格")
    value = Column(String(128), nullable=False, default="标准")
    image = Column(Text)


class GoodsProduct(Base):
    __tablename__ = "mal_goods_product"
    goods_id = Column(BigInteger, ForeignKey("mal_goods.id", ondelete="CASCADE"), nullable=False, index=True)
    specification = Column(String(128), nullable=False, default="标准")
    price = Column(Numeric(12, 2), nullable=False, default=0)
    quantity = Column(Integer, nullable=False, default=0)
    image = Column(Text)


class GoodsAttribute(Base):
    __tablename__ = "mal_goods_attribute"
    goods_id = Column(BigInteger, ForeignKey("mal_goods.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    value = Column(String(1000), nullable=False)
