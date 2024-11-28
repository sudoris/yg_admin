# -*- coding: utf-8 -*-
import enum
from typing import Any
from datetime import datetime
from .initialization_database import Base
from sqlalchemy import Column, Enum
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, DATETIME, TINYINT, TEXT, DATE, INTEGER, CHAR
from app_utility.encrypt_utility import BcryptUtility


privilege_dict = {
    101: 'Line訪客',
    110: '會員中心',
    200: '最新消息管理',
    300: '報名活動管理',
    400: '精品管理',
    410: '訂單管理',
    420: '輪播圖片管理',
    510: '會員卡管理',
    520: 'LOG管理',
    600: '權限管理',
    999: '系統管理員'
}


class UserStatus(enum.Enum):
    """ 店家帳號狀態 """
    NORMAL = '一般狀態'
    SUSPENDED = '停權'


class User(Base):
    """ 使用者 資料 Model """
    __tablename__ = 'usr_user'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)

    account = Column(VARCHAR(100))
    password = Column(CHAR(60), nullable=True)
    name = Column(VARCHAR(500), nullable=False)
    email = Column(VARCHAR(500), nullable=False, unique=True)
    status = Column(Enum(UserStatus), default=UserStatus.NORMAL)

    create_user_id = Column(BIGINT, nullable=True)
    create_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=True)
    update_datetime = Column(DATETIME, nullable=False)

    def create(self, account, password, name, email, status, user_id):
        self.account = account
        self.password = BcryptUtility.hash_password(password=password)
        self.name = name
        self.email = email
        self.status = status

        self.create_user_id = user_id
        self.update_user_id = user_id

        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update(self, name, email, status, editor_user_id):
        self.name = name
        self.email = email
        self.status = status

        self.update_user_id = editor_user_id
        self.update_datetime = datetime.now()

    def change_password(self, password: str):
        """ 變更密碼 """
        self.password = BcryptUtility.hash_password(password=password)
        self.update_datetime = datetime.now()

    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'account': self.account,
            'name': self.name,
            'email': self.email,
            'status': self.status.name
        }


class UserAndPrivilegeRelation(Base):
    """ 使用者與權限關聯 model """
    __tablename__ = 'usr_user_and_privilege_relation'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, nullable=False)
    privilege_id = Column(BIGINT, nullable=False)

    create_user_id = Column(BIGINT, nullable=True)
    create_datetime = Column(DATETIME, nullable=True)
    update_user_id = Column(BIGINT, nullable=True)
    update_datetime = Column(DATETIME, nullable=True)
    removed = Column(TINYINT, nullable=False, default=0)

    def __init__(self, user_id, privilege_id, create_user_id, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.privilege_id = privilege_id
        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

        self.create_user_id = create_user_id
        self.update_user_id = create_user_id

    def update(self, removed, user_id):
        self.removed = removed
        self.update_user_id = user_id
        self.update_datetime = datetime.now()


class UserLineInfo(Base):
    """ User Line 資訊 """
    __tablename__ = 'usr_user_line_info'
    TABLE = __tablename__

    line_user_id = Column(CHAR(33), primary_key=True)
    user_id = Column(BIGINT, nullable=True)
    operation = Column(VARCHAR(100), nullable=False, default='')
    flag_block = Column(TINYINT, nullable=False, default=0)

    create_datetime = Column(DATETIME, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)

    def create(self, line_user_id):
        self.line_user_id = line_user_id
        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update_user_id(self, user_id, operation):
        self.user_id = user_id
        self.operation = operation
        self.update_datetime = datetime.now()

    def follow(self):
        self.flag_block = 0
        self.update_datetime = datetime.now()

    def unfollow(self):
        self.flag_block = 1
        self.update_datetime = datetime.now()


class UserTmp(Base):
    __tablename__ = 'usr_user_tmp'
    TABLE = __tablename__

    line_user_id = Column(CHAR(33), primary_key=True)
    account = Column(VARCHAR(100), nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)

    def create(self, line_user_id, account):
        self.line_user_id = line_user_id
        self.account = account

        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update(self, account):
        self.account = account
        self.update_datetime = datetime.now()
