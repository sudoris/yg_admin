# -*- coding: utf-8 -*-
import enum
from typing import Any
from datetime import datetime
from .initialization_database import Base
from sqlalchemy import Column, Enum
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, DATETIME, TINYINT, TEXT, DATE, INTEGER, CHAR


class OrderStatus(enum.Enum):
    """ 訂單 狀態 """
    INITIAL = '建立'
    COMPLETE = '完成'
    CANCEL = '取消'


class Gender(enum.Enum):
    M = '男'
    F = '女'

class Payment(enum.Enum):
    POINTS = '扣點數'
    BALANCE = '扣儲值金'
    TRANSFER = '匯款'

class OrderPrimary(Base):

    __tablename__ = 'pr_product_order_primary'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    line_info_id = Column(BIGINT, nullable=False)
    member_id = Column(BIGINT, nullable=False)
    card_no = Column(VARCHAR(100), nullable=False)

    no = Column(CHAR(12), nullable=True, unique=True)
    total_price = Column(INTEGER, nullable=False, default=0)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.INITIAL)

    name = Column(VARCHAR(100), nullable=False, default='')
    gender = Column(Enum(Gender), nullable=True)
    mobile = Column(VARCHAR(100), nullable=False, default='')
    address = Column(VARCHAR(500), nullable=False, default='')
    payment_1 = Column(Enum(Payment), nullable=True)
    payment_2 = Column(Enum(Payment), nullable=True)
    payment_3 = Column(Enum(Payment), nullable=True)
    memo = Column(VARCHAR(4000), nullable=False, default='')
    remark = Column(VARCHAR(4000), nullable=False, default='')

    create_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=True)
    update_datetime = Column(DATETIME, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, line_info_id, member_id, card_no, name, gender, mobile, address, payment_1, payment_2, payment_3, memo, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.line_info_id = line_info_id
        self.member_id = member_id
        self.card_no = card_no

        self.name = name
        self.gender = gender if gender else None
        self.mobile = mobile
        self.address = address
        self.payment_1 = payment_1
        self.payment_2 = payment_2
        self.payment_3 = payment_3
        self.memo = memo

        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now


class OrderDetail(Base):

    __tablename__ = 'pr_product_order_detail'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    primary_id = Column(BIGINT, nullable=False)
    product_id = Column(BIGINT, nullable=False)
    price = Column(INTEGER, nullable=False, default=0)
    specific = Column(VARCHAR(100), nullable=False, default='')
    color = Column(VARCHAR(100), nullable=False, default='')
    quantity = Column(INTEGER, nullable=False, default=0)

    create_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=True)
    update_datetime = Column(DATETIME, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, primary_id, product_id, price, specific, color, quantity, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.primary_id = primary_id
        self.product_id = product_id
        self.price = price
        self.specific = specific
        self.color = color
        self.quantity = quantity

        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now


class ShopCartItem(Base):
    """ 購物車商品 """
    __tablename__ = 'pr_shop_cart_item'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    line_info_id = Column(BIGINT, nullable=False)
    product_id = Column(BIGINT, nullable=False)
    specific = Column(VARCHAR(100), nullable=False, default='')
    color = Column(VARCHAR(100), nullable=False, default='')
    quantity = Column(INTEGER, nullable=False, default=0)

    def __init__(self, line_info_id, product_id, specific, color, quantity, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.line_info_id = line_info_id
        self.product_id = product_id
        self.specific = specific
        self.color = color
        self.quantity = quantity



