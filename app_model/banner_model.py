# -*- coding: utf-8 -*-
from datetime import datetime
from .initialization_database import Base
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, DATETIME, INTEGER, TINYINT, DATE


class Banner(Base):
    """
    Banner 資料 Model
    """
    __tablename__ = 'sys_banner'
    TABLE = __tablename__

    id = Column(BIGINT, primary_key=True, autoincrement=True)

    title = Column(VARCHAR(1000), nullable=False)
    description = Column(VARCHAR(4000), nullable=False, default='')
    url = Column(VARCHAR(4000), nullable=True)
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE, nullable=False)
    seq = Column(INTEGER, nullable=False, default=9999)
    image_url = Column(VARCHAR(1000), nullable=True)

    create_user_id = Column(BIGINT, nullable=False)
    create_datetime = Column(DATETIME, nullable=False)
    update_user_id = Column(BIGINT, nullable=False)
    update_datetime = Column(DATETIME, nullable=False)
    removed = Column(TINYINT, nullable=False, default=0)

    def create(self, title, start_date, end_date, seq, create_user_id, url=None):
        self.title = title
        self.url = url
        self.start_date = start_date
        self.end_date = end_date
        self.seq = seq

        self.create_user_id = create_user_id
        self.update_user_id = create_user_id
        now = datetime.now()
        self.create_datetime = now
        self.update_datetime = now

    def update(self, title, start_date, end_date, seq, update_user_id, url=None):
        self.title = title
        self.url = url
        self.start_date = start_date
        self.end_date = end_date
        self.seq = seq
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()

    def delete(self, update_user_id):
        self.removed = 1
        self.update_user_id = update_user_id
        self.update_datetime = datetime.now()
