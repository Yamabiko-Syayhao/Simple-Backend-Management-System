# -*- coding: utf-8 -*-
"""模型公共基类（各业务模块的 model.py 继承 Base）"""
from app.models.base import Base, AssociationBase, DeclarativeRoot

__all__ = ["Base", "AssociationBase", "DeclarativeRoot"]
