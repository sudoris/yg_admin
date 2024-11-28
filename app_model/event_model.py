# -*- coding: utf-8 -*-
import enum
from typing import Any
from datetime import datetime
from .initialization_database import Base
from sqlalchemy import Column, Enum
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, DATETIME, TINYINT, TEXT, DATE, INTEGER, CHAR


class EventStatus(enum.Enum):
    """ Event 狀態 """
    NORMAL = '發布'
    SUSPENDED = '尚未發布'


class RegisterStatus(enum.Enum):
    """ 活動登記 狀態 """
    ACCEPT = '正取'
    WAITING = '備取'
    CANCEL = '取消'


class Payment(enum.Enum):
    POINTS = '扣點數'
    BALANCE = '扣儲值金'
    TRANSFER = '匯款'


class PaymentStatus(enum.Enum):
    """ 活動登記 狀態 """
    COMPLETE = '已繳款'
    INITIAL = '未繳款'
    REFUND = '已退款'


class EventPrimary(Base):
    """ 活動主檔 資料 Model """
    __tablename__ = 'ev_event_primary'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)

    title = Column(VARCHAR(500), nullable=False, default='')
    description = Column(VARCHAR(2000), nullable=False, default='')
    content = Column(TEXT, nullable=False)
    content_fee = Column(TEXT, nullable=False)
    content_refund = Column(TEXT, nullable=False)
    cover_image = Column(VARCHAR(500), nullable=False, default='')
    status = Column(Enum(EventStatus), nullable=False, default=EventStatus.NORMAL)
    flag_top = Column(TINYINT, nullable=False, default=0)
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE, nullable=False)

    create_user_id = Column(BIGINT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def create(self, title, description, content, content_fee, content_refund, status,
               flag_top, start_date, end_date, create_user_id):
        self.title = title
        self.description = description
        self.content = content
        self.content_fee = content_fee
        self.content_refund = content_refund
        self.flag_top = flag_top
        self.status = status
        self.start_date = start_date
        self.end_date = end_date

        self.create_user_id = create_user_id
        self.update_user_id = create_user_id
        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update(self, title, description, content, content_fee, content_refund, status, flag_top, start_date, end_date, update_user_id):
        self.title = title
        self.description = description
        self.content = content
        self.content_fee = content_fee
        self.content_refund = content_refund
        self.flag_top = flag_top
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()

    def delete(self, update_user_id):
        self.removed = 1
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()


class EventDetail(Base):
    """ 活動明細 """
    __tablename__ = 'ev_event_detail'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    primary_id = Column(BIGINT, nullable=False)
    location = Column(VARCHAR(1000), nullable=False, default='')
    time = Column(VARCHAR(1000), nullable=False, default='')
    limit = Column(INTEGER, nullable=False, default=0)
    end_date = Column(DATE, nullable=True)

    create_user_id = Column(BIGINT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)

    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, primary_id, location, time, limit, end_date, create_user_id, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.primary_id = primary_id
        self.location = location
        self.time = time
        self.limit = limit
        self.end_date = end_date
        self.create_user_id = create_user_id
        self.update_user_id = create_user_id

        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update(self, location, time, limit, end_date, update_user_id):
        self.location = location
        self.time = time
        self.limit = limit
        self.end_date = end_date
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()

    def delete(self, update_user_id):
        self.removed = 1
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()


class RegisterPrimary(Base):
    __tablename__ = 'ev_register_primary'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    event_detail_id = Column(BIGINT, nullable=False)  # 場次
    line_info_id = Column(BIGINT, nullable=False)
    member_id = Column(BIGINT, nullable=False)
    card_no = Column(VARCHAR(100), nullable=False)
    status = Column(Enum(RegisterStatus), nullable=False, default=RegisterStatus.WAITING)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.INITIAL)

    payment_1 = Column(Enum(Payment), nullable=True)
    payment_2 = Column(Enum(Payment), nullable=True)
    payment_3 = Column(Enum(Payment), nullable=True)

    create_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=True)
    update_datetime = Column(DATETIME, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, event_detail_id, line_info_id, member_id, card_no,
                 status, payment_1, payment_2, payment_3, *args: Any,
                 **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.event_detail_id = event_detail_id
        self.line_info_id = line_info_id
        self.member_id = member_id
        self.card_no = card_no
        self.status = status

        self.payment_1 = payment_1
        self.payment_2 = payment_2
        self.payment_3 = payment_3

        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now


class RegisterFamily(Base):
    __tablename__ = 'ev_register_family'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    primary_id = Column(BIGINT, nullable=False)
    name = Column(VARCHAR(100), nullable=False, default='')
    card_no = Column(VARCHAR(100), nullable=False, default='')
    status = Column(Enum(RegisterStatus),
                    nullable=False,
                    default=RegisterStatus.WAITING)

    create_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=True)
    update_datetime = Column(DATETIME, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, primary_id, name, card_no, status, *args: Any,
                 **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.primary_id = primary_id
        self.name = name
        self.card_no = card_no
        self.status = status

        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update(self, primary_id, name, card_no, status, update_user_id):
        self.primary_id = primary_id
        self.name = name
        self.card_no = card_no
        self.status = status

        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()

    def delete(self, update_user_id):
        self.removed = 1
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()


class RegisterGuest(Base):
    __tablename__ = 'ev_register_guest'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    primary_id = Column(BIGINT, nullable=False)
    name = Column(VARCHAR(100), nullable=False, default='')
    status = Column(Enum(RegisterStatus),
                    nullable=False,
                    default=RegisterStatus.WAITING)

    create_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=True)
    update_datetime = Column(DATETIME, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, primary_id, name, status, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.primary_id = primary_id
        self.name = name
        self.status = status

        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update(self, primary_id, name, status, update_user_id):
        self.primary_id = primary_id
        self.name = name
        self.status = status

        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()

    def delete(self, update_user_id):
        self.removed = 1
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()


class Interest(Base):
    __tablename__ = 'ev_interest'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(1000), nullable=False, default='')


class EventAndInterestRelation(Base):
    __tablename__ = 'ev_interest_and_event_relation'
    TABLE = __tablename__

    event_id = Column(BIGINT, nullable=False, primary_key=True)
    interest_id = Column(BIGINT, nullable=False, primary_key=True)
    removed = Column(TINYINT, default=0)

    def create(self, event_id, interest_id):
        self.event_id = event_id
        self.interest_id = interest_id

    def update(self, removed):
        self.removed = removed
