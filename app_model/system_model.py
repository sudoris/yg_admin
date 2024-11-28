# -*- coding: utf-8 -*-
import enum
from datetime import datetime
from .initialization_database import Base
from sqlalchemy import Column, Enum
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, DATETIME, TINYINT, TEXT, DATE, INTEGER, CHAR


class MemberCard(Base):
    """ 會員卡片設定 """
    __tablename__ = 'system_member_card'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(1000), nullable=False, default='')
    code = Column(VARCHAR(100), nullable=False, default='')
    image_url = Column(VARCHAR(1000), nullable=True)

    create_user_id = Column(BIGINT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def create(self, title, code, create_user_id):
        self.title = title
        self.code = code
        self.create_user_id = create_user_id
        self.update_user_id = create_user_id
        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update(self, title, code, update_user_id):
        self.title = title
        self.code = code
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()


class MenuType(enum.Enum):
    """ 選單類別 """
    LOGIN = '登入'
    UNLOGIN = '未登入'


class RichMenu(Base):
    """ 組織 RichMenu 紀錄 """
    __tablename__ = 'system_rich_menu'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    menu_type = Column(Enum(MenuType), nullable=False)

    menu_id = Column(VARCHAR(500), nullable=False)
    content = Column(VARCHAR(5000), nullable=False)
    image_url = Column(VARCHAR(1000), nullable=False)

    create_user_id = Column(BIGINT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def create(self, menu_type, menu_id, content, image_url, create_user_id):
        self.menu_type = menu_type
        self.menu_id = menu_id
        self.content = content
        self.image_url = image_url
        now = datetime.now()
        self.create_user_id = create_user_id
        self.update_user_id = create_user_id
        self.create_datetime = now
        self.update_datetime = now

    def delete(self, update_user_id):
        self.removed = 1
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()
