# -*- coding: utf-8 -*-
from typing import Optional, List
from app_service.core_service import CoreService
from app_model.log_model import AthenaApiLog, AppApiLog, SMSHistory


class LogService(CoreService):

    def find_athena_api_log_by_criteria(self, criteria: dict, page: int, row_per_page: int):
        db_session = self.db_session
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)

        if criteria.get('date_start', None):
            criteria['datetime_start'] = criteria['date_start'] + ' 00:00:00'

        if criteria.get('date_end', None):
            criteria['datetime_end'] = criteria['date_end'] + ' 23:59:59'

        sql = "  SELECT COUNT(log.id) "
        sql += " FROM " + AthenaApiLog.TABLE + " log "
        sql += " WHERE 1 = 1 "
        if criteria.get('datetime_start', None):
            sql += " AND log.create_datetime >= :datetime_start "
        if criteria.get('datetime_end', None):
            sql += " AND log.create_datetime <= :datetime_end "
        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT log.* "
        sql += " FROM " + AthenaApiLog.TABLE + " log "
        sql += " WHERE 1 = 1 "
        if criteria.get('datetime_start', None):
            sql += " AND log.create_datetime >= :datetime_start "
        if criteria.get('datetime_end', None):
            sql += " AND log.create_datetime <= :datetime_end "
        sql += " ORDER BY id DESC "
        sql += " LIMIT :index, :count "
        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list

    def find_app_api_log_by_criteria(self, criteria: dict, page: int, row_per_page: int):
        db_session = self.db_session
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)

        if criteria.get('date_start', None):
            criteria['datetime_start'] = criteria['date_start'] + ' 00:00:00'

        if criteria.get('date_end', None):
            criteria['datetime_end'] = criteria['date_end'] + ' 23:59:59'

        sql = "  SELECT COUNT(log.id) "
        sql += " FROM " + AppApiLog.TABLE + " log "
        sql += " WHERE 1 = 1 "
        if criteria.get('datetime_start', None):
            sql += " AND log.create_datetime >= :datetime_start "
        if criteria.get('datetime_end', None):
            sql += " AND log.create_datetime <= :datetime_end "
        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT log.* "
        sql += " FROM " + AppApiLog.TABLE + " log "
        sql += " WHERE 1 = 1 "
        if criteria.get('datetime_start', None):
            sql += " AND log.create_datetime >= :datetime_start "
        if criteria.get('datetime_end', None):
            sql += " AND log.create_datetime <= :datetime_end "
        sql += " ORDER BY id DESC "
        sql += " LIMIT :index, :count "
        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list

    def find_last_sms_history_by_mobile(self, mobile) -> Optional[SMSHistory]:
        db_session = self.db_session
        history = db_session.query(SMSHistory).filter(SMSHistory.mobile == mobile).order_by(SMSHistory.id.desc()).first()
        return history

    def find_sms_history_by_criteria(self, criteria: dict, page: int, row_per_page: int):
        db_session = self.db_session
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)
        if criteria.get('mobile', None):
            criteria['mobile'] = '%' + criteria['mobile'] + '%'

        if criteria.get('date_start', None):
            criteria['datetime_start'] = criteria['date_start'] + ' 00:00:00'

        if criteria.get('date_end', None):
            criteria['datetime_end'] = criteria['date_end'] + ' 23:59:59'

        sql = "  SELECT COUNT(log.id) "
        sql += " FROM " + SMSHistory.TABLE + " log "
        sql += " WHERE 1 = 1 "
        if criteria.get('mobile', None):
            sql += " AND log.mobile LIKE :mobile "
        if criteria.get('datetime_start', None):
            sql += " AND log.create_datetime >= :datetime_start "
        if criteria.get('datetime_end', None):
            sql += " AND log.create_datetime <= :datetime_end "
        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT log.* "
        sql += " FROM " + SMSHistory.TABLE + " log "
        sql += " WHERE 1 = 1 "
        if criteria.get('mobile', None):
            sql += " AND log.mobile LIKE :mobile "
        if criteria.get('datetime_start', None):
            sql += " AND log.create_datetime >= :datetime_start "
        if criteria.get('datetime_end', None):
            sql += " AND log.create_datetime <= :datetime_end "
        sql += " ORDER BY id DESC "
        sql += " LIMIT :index, :count "
        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list



