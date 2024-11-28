# -*- coding: utf-8 -*-
from flask import g
from app_model.initialization_database import get_db_session


class CoreService:

    def __init__(self, db_session=None):
        """ 如果 沒有傳入 db_session 會自動 優先從 flask 的 global request context 取出， 再如果沒有才會自動連線取得新的 """
        if db_session:
            self.db_session = db_session
        elif hasattr(g, 'db_session'):
            self.db_session = g.db_session
        else:
            self.db_session = get_db_session()

    def build_criteria_range(self, criteria, page, row_per_page):
        if not isinstance(criteria, dict):
            raise Exception('Criteria Must Be a Dict')
        index = (page - 1) * row_per_page
        criteria['index'] = index
        criteria['count'] = row_per_page
