# -*- coding: utf-8 -*-
from typing import Optional, Tuple, List, Dict
from app_service.core_service import CoreService
from app_model.news_model import News


class NewsService(CoreService):

    def find_news_by_id(self, media_id: int) -> Optional[News]:
        """ 以 id 取得 News """
        db_session = self.db_session
        news = db_session.query(News).filter_by(id=media_id).first()
        return news

    def find_news_by_line_keyword(self, line_keyword: str) -> Optional[News]:
        """ 以 line_keyword 取得 News """
        db_session = self.db_session
        news = db_session.query(News).filter_by(line_keyword=line_keyword).first()
        return news

    def find_news_by_criteria(self, criteria: dict, page: int, row_per_page: int, order_by: str=''):
        db_session = self.db_session
        if criteria.get('title', None):
            criteria['title'] = '%' + criteria['title'] + '%'

        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)

        sql = "  SELECT COUNT(news.id) "
        sql += " FROM " + News.TABLE + " news "
        sql += " WHERE news.removed = 0 "
        if criteria.get('title', None):
            sql += " AND news.title LIKE :title "
        if criteria.get('status', None):
            sql += " AND news.status = :status "
        if criteria.get('flag_visitor', None) is not None:
            sql += " AND news.flag_visitor = 1 "
        if criteria.get('flag_member', None) is not None:
            sql += " AND news.flag_member = 1 "
        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT news.* "
        sql += " FROM " + News.TABLE + " news "
        sql += " WHERE news.removed = 0 "
        if criteria.get('title', None):
            sql += " AND news.title LIKE :title "
        if criteria.get('status', None):
            sql += " AND news.status = :status "
        if criteria.get('flag_visitor', None) is not None:
            sql += " AND news.flag_visitor = 1 "
        if criteria.get('flag_member', None) is not None:
            sql += " AND news.flag_member = 1 "
        if order_by == 'display_date':
            sql += " ORDER BY news.flag_top DESC, news.display_date DESC "
        else:
            sql += " ORDER BY news.update_datetime DESC "
        sql += " LIMIT :index, :count "

        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list
