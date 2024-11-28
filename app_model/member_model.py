# -*- coding: utf-8 -*-
from typing import Any
from datetime import datetime
from .initialization_database import Base
from sqlalchemy import Column, Enum
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, DATETIME, TINYINT, TEXT, DATE, INTEGER, CHAR
from app_utility.string_utility import StringUtility


class MemberTmp(Base):
    __tablename__ = 'mem_member_tmp'
    TABLE = __tablename__

    line_user_id = Column(CHAR(33), nullable=False, primary_key=True)
    identify_no = Column(VARCHAR(100), nullable=True)
    card_no = Column(VARCHAR(100), nullable=True)
    member_mobile = Column(VARCHAR(100), nullable=True) # 會員資料-手機號碼
    mobile = Column(VARCHAR(100), nullable=True) # 目前使用者手機號碼

    code = Column(CHAR(6), nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)

    def create(self, line_user_id, identify_no, card_no, member_mobile):
        self.line_user_id = line_user_id
        self.identify_no = identify_no
        self.card_no = card_no
        self.member_mobile = member_mobile

        self.code = StringUtility.generate_random_number(6)
        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update(self, identify_no, card_no, member_mobile):
        self.identify_no = identify_no
        self.card_no = card_no
        self.member_mobile = member_mobile
        self.code = StringUtility.generate_random_number(6)
        self.update_datetime = datetime.now()

class MemberLineInfo(Base):
    __tablename__ = 'mem_line_info'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    line_user_id = Column(CHAR(33), nullable=False, unique=True)
    display_name = Column(VARCHAR(500), nullable=True)
    picture_url = Column(VARCHAR(1000), nullable=True)

    member_id = Column(BIGINT, nullable=True) # 綁定的會員 身份証號/護照號碼
    card_no = Column(VARCHAR(100), nullable=True) # 當下切換的卡號
    mobile = Column(VARCHAR(20), nullable=True) # 驗證過的手機號碼

    operation = Column(VARCHAR(100), nullable=False, default='')
    flag_block = Column(TINYINT, nullable=False, default=0)
    status = Column(TINYINT, nullable=False, default=0)

    create_datetime = Column(DATETIME, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)

    def create(self, line_user_id):
        self.line_user_id = line_user_id
        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def follow(self):
        self.flag_block = 0
        self.update_datetime = datetime.now()

    def unfollow(self):
        self.flag_block = 1
        self.update_datetime = datetime.now()


class Member(Base):
    __tablename__ = 'mem_member'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    identify_no = Column(VARCHAR(100), nullable=False, unique=True)
    no = Column(VARCHAR(100), nullable=False, default='') # 會籍編號
    name = Column(VARCHAR(100), nullable=False, default='') # 會員姓名
    remark = Column(TEXT, nullable=False, default='')
    interest_1 = Column(INTEGER, nullable=False, default=0)
    interest_2 = Column(INTEGER, nullable=False, default=0)
    interest_3 = Column(INTEGER, nullable=False, default=0)
    interest_4 = Column(INTEGER, nullable=False, default=0)
    interest_5 = Column(INTEGER, nullable=False, default=0)
    interest_6 = Column(INTEGER, nullable=False, default=0)
    interest_7 = Column(INTEGER, nullable=False, default=0)
    interest_8 = Column(INTEGER, nullable=False, default=0)
    interest_9 = Column(INTEGER, nullable=False, default=0)
    interest_10 = Column(INTEGER, nullable=False, default=0)

    def create(self, identify_no):
        self.identify_no = identify_no

class MemberLineInfoAuthToken(Base):
    __tablename__ = 'mem_line_info_auth_token'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    line_info_id = Column(BIGINT, nullable=False)
    token = Column(VARCHAR(150), nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, line_info_id, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.line_info_id = line_info_id
        self.token = StringUtility.generate_random_number_and_lowercase_letters(150)
        self.create_datetime = datetime.now()


class MemberMessage(Base):
    __tablename__ = 'mem_member_message'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    order_id = Column(BIGINT, nullable=True)
    event_detail_id = Column(BIGINT, nullable=True)
    card_no = Column(VARCHAR(100), nullable=False)
    title = Column(VARCHAR(100), nullable=False, default='')
    description = Column(VARCHAR(1000), nullable=False, default='')
    content = Column(TEXT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    read_datetime = Column(DATETIME, nullable=True)
    removed = Column(TINYINT, nullable=False, default=0)

    def create(self, card_no, title, description, content, order_id=None, event_detail_id=None):
        self.order_id = order_id
        self.event_detail_id = event_detail_id
        self.card_no = card_no
        self.title = title
        self.description = description
        self.content = content
        self.create_datetime = datetime.now()

