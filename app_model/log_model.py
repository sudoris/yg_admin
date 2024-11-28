# -*- coding: utf-8 -*-
from typing import Any
from datetime import datetime
from .initialization_database import Base
from sqlalchemy import Column, Enum
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, DATETIME, TINYINT, TEXT, DATE, INTEGER, CHAR


class LoginHistory(Base):
    """
    使用者登入紀錄 資料 Model
    """
    __tablename__ = 'log_login_history'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    admin_id = Column(BIGINT, nullable=True)
    admin_account = Column(VARCHAR(100), nullable=True)
    user_id = Column(BIGINT, nullable=True)
    user_account = Column(VARCHAR(100), nullable=True)
    member_id = Column(VARCHAR(100), nullable=True)
    member_account = Column(VARCHAR(100), nullable=True)
    result = Column(TINYINT, nullable=False, default=False)
    ip = Column(VARCHAR(500), nullable=False)
    create_datetime = Column(DATETIME, nullable=False)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    def create_admin_login_log(self, admin_id, admin_account, ip, result):
        self.admin_id = admin_id
        self.admin_account = admin_account
        self.ip = ip
        self.result = result
        self.create_datetime = datetime.now()

    def create_user_login_log(self, user_id, user_account, ip, result):
        self.user_id = user_id
        self.user_account = user_account
        self.ip = ip
        self.result = result
        self.create_datetime = datetime.now()

    def create_member_login_log(self, member_id, member_account, ip, result):
        self.member_id = member_id
        self.member_account = member_account
        self.ip = ip
        self.result = result
        self.create_datetime = datetime.now()


class AthenaApiLog(Base):
    """ 德安API呼叫紀錄 """
    __tablename__ = 'log_athena_api'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    url = Column(VARCHAR(1000), nullable=False)
    request_body = Column(TEXT, nullable=True)
    response_body = Column(TEXT, nullable=True)
    create_datetime = Column(DATETIME, nullable=False)

    def __init__(self, url, request_body, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.url = url
        self.request_body = request_body
        self.create_datetime = datetime.now()

class AppApiLog(Base):
    """ App API呼叫紀錄 """
    __tablename__ = 'log_app_api'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    line_info_id = Column(BIGINT, nullable=True)
    url = Column(VARCHAR(1000), nullable=False)
    request_body = Column(TEXT, nullable=True)
    response_body = Column(TEXT, nullable=True)
    ip = Column(VARCHAR(500), nullable=True)
    create_datetime = Column(DATETIME, nullable=False)

    def __init__(self, url, request_body, ip=None, line_info_id=None, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.line_info_id = line_info_id
        self.url = url
        self.request_body = request_body
        self.ip = ip
        self.create_datetime = datetime.now()


class SMSHistory(Base):
    """ 簡訊紀錄 """
    __tablename__ = 'log_sms_history'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    mobile = Column(CHAR(10), nullable=False)
    content = Column(VARCHAR(500), nullable=False)
    create_datetime = Column(DATETIME, nullable=False)

    def __init__(self, mobile, content, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.mobile = mobile
        self.content = content
        self.create_datetime = datetime.now()
