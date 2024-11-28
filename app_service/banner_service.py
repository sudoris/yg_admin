# -*- coding: utf-8 -*-
from typing import Optional
from app_service.core_service import CoreService
from app_model.banner_model import Banner


class BannerService(CoreService):

    def find_banner_by_id(self, banner_id) -> Optional[Banner]:
        """ 以 id 搜尋 Banner """
        db_session = self.db_session
        banner = db_session.query(Banner).filter_by(id=banner_id).first()
        return banner

    def find_active_banner(self):
        db_session = self.db_session
        sql = "  SELECT banner.id, banner.image_url, banner.url "
        sql += " FROM " + Banner.TABLE + " banner "
        sql += " WHERE banner.removed = 0 AND banner.image_url IS NOT NULL "
        sql += " AND NOW() >= banner.start_date AND DATE_SUB( NOW(), INTERVAL 1 DAY)  <= banner.end_date "
        sql += " ORDER BY banner.seq ASC "
        results = db_session.execute(sql, {})
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return item_list

    def find_banner_by_criteria(self, criteria: dict, page: int, row_per_page: int):
        db_session = self.db_session

        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)

        sql = "  SELECT COUNT(banner.id) "
        sql += " FROM " + Banner.TABLE + " banner "
        sql += " WHERE banner.removed = 0 "
        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT banner.* "
        sql += " FROM " + Banner.TABLE + " banner "
        sql += " WHERE banner.removed = 0 "
        sql += " ORDER BY banner.seq ASC "
        sql += " LIMIT :index, :count "

        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list
