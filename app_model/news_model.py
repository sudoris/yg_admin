# -*- coding: utf-8 -*-
import enum
from typing import Any
from datetime import datetime
from .initialization_database import Base
from sqlalchemy import Column, Enum
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, DATETIME, TINYINT, TEXT, DATE, INTEGER, CHAR


class NewsStatus(enum.Enum):
    """
    最新消息 狀態
    """
    NORMAL = '發布'
    SUSPENDED = '尚未發布'


class News(Base):
    """
    最新消息 資料 Model
    """
    __tablename__ = 'info_news'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(500), nullable=False, default='')
    description = Column(VARCHAR(2000), nullable=False, default='')
    cover_image = Column(VARCHAR(500), nullable=False, default='')
    content = Column(TEXT)

    line_keyword = Column(VARCHAR(500), nullable=True) # Line 回覆關鍵字
    flag_top = Column(TINYINT, nullable=False, default=0)
    display_date = Column(DATE, nullable=False)
    status = Column(Enum(NewsStatus), nullable=False, default=NewsStatus.NORMAL)
    flag_visitor = Column(TINYINT, nullable=False, default=0)
    flag_member = Column(TINYINT, nullable=False, default=0)  # 會員

    create_user_id = Column(BIGINT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def create(self, title, description, content, status, flag_top, display_date, flag_visitor, flag_member, line_keyword, create_user_id):
        self.title = title
        self.description = description
        self.content = content
        self.status = status
        self.flag_top = flag_top
        self.display_date = display_date
        self.flag_visitor = flag_visitor
        self.flag_member = flag_member
        self.line_keyword = line_keyword.strip()

        now = datetime.now()
        self.create_user_id = create_user_id
        self.update_user_id = create_user_id
        self.create_datetime = now
        self.update_datetime = now

    def update(self, title, description, content, status, flag_top, display_date, flag_visitor, flag_member, line_keyword, update_user_id):
        self.title = title
        self.description = description
        self.content = content
        self.status = status
        self.flag_top = flag_top
        self.flag_visitor = flag_visitor
        self.flag_member = flag_member
        self.line_keyword = line_keyword.strip()

        self.display_date = display_date
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()

    def delete(self, update_user_id):
        self.update_user_id = update_user_id
        self.removed = 1
        self.update_datetime = datetime.now()

