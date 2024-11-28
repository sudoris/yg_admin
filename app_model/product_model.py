# -*- coding: utf-8 -*-
import enum
from typing import Any
from datetime import datetime
from .initialization_database import Base
from sqlalchemy import Column, Enum
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, DATETIME, TINYINT, TEXT, DATE, INTEGER, CHAR


class ProductStatus(enum.Enum):
    """ 商品 狀態 """
    NORMAL = '上架'
    SUSPENDED = '下架'


class ProductColor(Base):
    """ 商品顏色 """
    __tablename__ = 'pt_product_color'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(500), nullable=False)
    code = Column(VARCHAR(100), nullable=False)

    create_user_id = Column(BIGINT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, title, create_user_id, code=None, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.title = title
        self.code = code
        self.create_user_id = create_user_id
        self.update_user_id = create_user_id
        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update(self, title, code, user_id):
        self.title = title
        self.code = code
        self.update_user_id = user_id
        self.update_datetime = datetime.now()

class ProductCategory(Base):
    """ 商品類別 """
    __tablename__ = 'pt_product_category'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(500), nullable=False)
    description = Column(VARCHAR(500), nullable=False, default='')

    create_user_id = Column(BIGINT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)


class Product(Base):
    """ 商品主檔 """
    __tablename__ = 'pt_product'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    category_id = Column(BIGINT, nullable=True)
    title = Column(VARCHAR(500), nullable=False)
    description = Column(VARCHAR(3000), nullable=False, default='')
    content = Column(TEXT, nullable=True)
    price = Column(INTEGER, nullable=False, default=0)
    status = Column(Enum(ProductStatus), nullable=False, default=ProductStatus.NORMAL)
    seq = Column(INTEGER, nullable=False, default=9999)

    create_user_id = Column(BIGINT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, category_id, title, content, price, status, create_user_id, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.category_id = category_id
        self.title = title
        self.price = price
        self.content = content
        self.status = status

        self.create_user_id = create_user_id
        self.update_user_id = create_user_id
        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update(self, category_id, title, content, price, status, update_user_id):
        self.category_id = category_id
        self.title = title
        self.content = content
        self.price = price
        self.status = status
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()


class ProductImage(Base):
    """ 產品圖片 """
    __tablename__ = 'pt_product_image'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    product_id = Column(BIGINT, nullable=True)
    image_url = Column(VARCHAR(500), nullable=False)
    seq = Column(INTEGER, nullable=False, default=9999)
    alt = Column(VARCHAR(500), nullable=False, default='')
    flag_cover = Column(TINYINT, nullable=False, default=0)

    create_user_id = Column(BIGINT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, image_url, create_user_id, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.image_url = image_url
        self.create_user_id = create_user_id
        self.update_user_id = create_user_id
        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def delete(self, update_user_id):
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()
        self.removed = 1

class ProductColorImage(Base):
    """ 產品圖片顏色 """
    __tablename__ = 'pt_product_color_image'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    product_id = Column(BIGINT, nullable=False)
    color = Column(VARCHAR(100), nullable=False)
    image_url = Column(VARCHAR(500), nullable=True)

    create_user_id = Column(BIGINT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, product_id, color, image_url, create_user_id, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.product_id = product_id
        self.color = color
        self.image_url = image_url

        now = datetime.now()
        self.create_user_id = create_user_id
        self.update_user_id = create_user_id
        self.create_datetime = now
        self.update_datetime = now

    def update(self, image_url, update_user_id):
        self.image_url = image_url
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()

    def delete(self, update_user_id):
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()
        self.removed = 1

class ProductSpecific(Base):
    """ 產品規格 """
    __tablename__ = 'pt_product_specific'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    product_id = Column(BIGINT, nullable=False)
    title = Column(VARCHAR(500), nullable=False)    # 規格
    color_list = Column(VARCHAR(500), nullable=False) # 顏色清單

    create_user_id = Column(BIGINT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, product_id, title, color_list, create_user_id, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.product_id = product_id
        self.title = title
        self.color_list = color_list
        self.create_user_id = create_user_id
        self.update_user_id = create_user_id

        now =  datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update(self, color_list, update_user_id):
        self.color_list = color_list
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()

    def delete(self, update_user_id):
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()
        self.removed = 1



