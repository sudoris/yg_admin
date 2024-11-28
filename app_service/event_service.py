# -*- coding: utf-8 -*-
from typing import Optional, Tuple, List, Dict, AnyStr
from app_service.core_service import CoreService
from app_model.event_model import EventPrimary, EventDetail, RegisterPrimary, RegisterFamily, RegisterGuest, Interest, EventAndInterestRelation
from app_model.member_model import Member


class EventService(CoreService):

    def find_event_primary_by_id(self, primary_id) -> Optional[EventPrimary]:
        """ 以 id 取得 Event """
        db_session = self.db_session
        event = db_session.query(EventPrimary).filter_by(id=primary_id).first()
        return event

    def find_event_primary_by_criteria(self, criteria: dict, page: int, row_per_page: int) -> Tuple:

        db_session = self.db_session
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)

        if criteria.get('title', None):
            criteria['title'] = '%' + criteria['title'] + '%'

        sql = "  SELECT COUNT(event.id) "
        sql += " FROM " + EventPrimary.TABLE + " event "
        sql += " WHERE 1 = 1 "
        if criteria.get('title', None):
            sql += " AND event.title LIKE :title "
        if criteria.get('status', None):
            sql += " AND event.status = :status "
        if criteria.get('removed', None) is not None:
            sql += " AND event.removed = :removed "

        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT event.* "
        sql += " FROM " + EventPrimary.TABLE + " event "
        sql += " WHERE 1 = 1 "
        if criteria.get('title', None):
            sql += " AND event.title LIKE :title "
        if criteria.get('status', None):
            sql += " AND event.status = :status "
        if criteria.get('removed', None):
            sql += " AND event.removed = :removed "

        sql += " ORDER BY "
        sql += "       flag_top DESC, "
        sql += "       start_date DESC "
        sql += " LIMIT :index, :count "

        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list

    def api_find_event_by_criteria(self, criteria: dict, page: int, row_per_page: int) -> Tuple:
        db_session = self.db_session
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)

        sql = "  SELECT COUNT(event.id) "
        sql += " FROM " + EventPrimary.TABLE + " event "
        sql += " WHERE 1 = 1 "
        if criteria.get('removed', None):
            sql += " AND event.removed = :removed "
        if criteria.get('status', None):
            sql += " AND event.status = :status "

        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT event.id, event.cover_image, event.title, event.description, event.start_date, event.end_date "
        sql += " FROM " + EventPrimary.TABLE + " event "
        sql += " WHERE 1 = 1 "
        if criteria.get('removed', None):
            sql += " AND event.removed = :removed "
        if criteria.get('status', None):
            sql += " AND event.status = :status "

        sql += " ORDER BY "
        sql += "       flag_top DESC, "
        sql += "       start_date DESC "
        sql += " LIMIT :index, :count "

        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list

    def find_event_detail_by_id(self, detail_id) -> Optional[EventDetail]:
        """ 以 id 取得 Event """
        db_session = self.db_session
        detail = db_session.query(EventDetail).filter_by(id=detail_id).first()
        return detail

    def calculate_event_detail_remain(self, detail_id) -> int:
        db_session = self.db_session
        detail = self.find_event_detail_by_id(detail_id)
        if not detail or detail.removed:
            return 0

        primary_id_list = []
        primary_list = db_session.query(RegisterPrimary).filter_by(
            event_detail_id=detail_id, status='ACCEPT', removed=0).all()
        for primary in primary_list:
            primary_id_list.append(primary.id)

        count = len(primary_id_list)
        family_list = db_session.query(RegisterFamily).filter(
            RegisterFamily.primary_id.in_(primary_id_list),
            RegisterFamily.status == 'ACCEPT',
            RegisterFamily.removed == 0).all()
        quest_list = db_session.query(RegisterGuest).filter(
            RegisterGuest.primary_id.in_(primary_id_list),
            RegisterGuest.status == 'ACCEPT',
            RegisterGuest.removed == 0).all()

        count += len(family_list)
        count += len(quest_list)

        return detail.limit - count

    def find_all_event_detail_by_primary_id(self, primary_id) -> List[EventDetail]:
        """ 以 primary_id 取得 EventDetail """
        db_session = self.db_session
        event_detail_list = db_session.query(EventDetail).filter_by(primary_id=primary_id, removed=0).all()
        return event_detail_list

    def find_event_detail_by_primary_id_and_page(self, primary_id: int,
                                                 criteria: dict, page: int,
                                                 row_per_page: int) -> Tuple:
        db_session = self.db_session
        self.build_criteria_range(criteria=criteria,
                                  page=page,
                                  row_per_page=row_per_page)

        sql = "  SELECT COUNT(event.id) "
        sql += " FROM " + EventDetail.TABLE + " event "
        sql += " WHERE 1 = 1 "
        sql += " AND event.primary_id = " + str(primary_id)
        sql += " AND event.removed = 0 "
        if criteria.get('status', None):
            sql += " AND event.status = :status "

        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT event.* "
        sql += " FROM " + EventDetail.TABLE + " event "
        sql += " WHERE 1 = 1 "
        sql += " AND event.primary_id = " + str(primary_id)
        sql += " AND event.removed = 0 "
        if criteria.get('status', None):
            sql += " AND event.status = :status "

        sql += " LIMIT :index, :count "

        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list

    def find_register_primary_by_id(self, primary_id) -> Optional[RegisterPrimary]:
        """ 以 id 取得 Register """
        db_session = self.db_session
        register = db_session.query(RegisterPrimary).filter_by(
            id=primary_id).first()
        return register

    def find_register_primary_by_event_detail_id_and_card_no(
            self, event_detail_id, card_no) -> Optional[RegisterPrimary]:
        db_session = self.db_session
        primary = db_session.query(RegisterPrimary).filter_by(
            event_detail_id=event_detail_id, card_no=card_no,
            removed=0).first()
        return primary

    def find_register_primary_by_event_detail_id_and_page(self, event_detail_id: int, criteria: dict, page: int, row_per_page: int) -> Tuple:
        db_session = self.db_session
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)

        if criteria.get('card_no', None):
            criteria['card_no'] = '%' + criteria['card_no'] + '%'

        sql = "  SELECT COUNT(register.id) "
        sql += " FROM " + RegisterPrimary.TABLE + " register "
        sql += " WHERE 1 = 1 "
        sql += " AND register.event_detail_id = " + str(event_detail_id)
        sql += " AND register.removed = 0 "
        if criteria.get('card_no', None):
            sql += " AND register.card_no LIKE :card_no "
        if criteria.get('status', None):
            sql += " AND register.status = :status "
        if criteria.get('payment_status', None):
            sql += " AND register.payment_status = :payment_status "

        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT register.*, member.id AS mem_member_id, member.no AS mem_member_no, member.name "
        sql += " FROM " + RegisterPrimary.TABLE + " register "
        sql += " INNER JOIN " + Member.TABLE + " member ON member.id = register.member_id"
        sql += " WHERE 1 = 1 "
        sql += " AND register.event_detail_id = " + str(event_detail_id)
        sql += " AND register.removed = 0 "
        if criteria.get('card_no', None):
            sql += " AND register.card_no LIKE :card_no "
        if criteria.get('status', None):
            sql += " AND register.status = :status "
        if criteria.get('payment_status', None):
            sql += " AND register.payment_status = :payment_status "
        sql += " LIMIT :index, :count "

        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list

    def find_register_primary_by_event_detail_id_and_payment_status(self, event_detail_id: int, payment_status: str) -> List[RegisterPrimary]:
        db_session = self.db_session
        query = db_session.query(RegisterPrimary).filter_by(event_detail_id=event_detail_id, removed=0)
        if payment_status == 'INITIAL':
            query = query.filter_by(payment_status='INITIAL')
        elif payment_status == 'COMPLETE':
            query = query.filter_by(payment_status='COMPLETE')
        register_primary_list = query.all()
        return register_primary_list

    def find_register_family_by_id(self, id) -> Optional[RegisterFamily]:
        """ 以 id 取得 RegisterFamily """
        db_session = self.db_session
        register = db_session.query(RegisterFamily).filter_by(id=id).first()
        return register

    def find_register_guest_by_id(self, id) -> Optional[RegisterGuest]:
        """ 以 id 取得 RegisterGuest """
        db_session = self.db_session
        register = db_session.query(RegisterGuest).filter_by(id=id).first()
        return register

    def find_register_family_by_primary_id(self, primary_id: int) -> Tuple:
        db_session = self.db_session

        sql = "  SELECT COUNT(`register`.id) "
        sql += " FROM " + RegisterFamily.TABLE + " `register` "
        sql += " WHERE 1 = 1 "
        sql += " AND removed = 0 "
        sql += " AND primary_id = " + str(primary_id)
        total_count = db_session.execute(sql).fetchone()[0]

        sql = "  SELECT `register`.* "
        sql += " FROM " + RegisterFamily.TABLE + " `register` "
        sql += " WHERE 1 = 1 "
        sql += " AND removed = 0 "
        sql += " AND primary_id = " + str(primary_id)

        results = db_session.execute(sql)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list

    def find_register_guest_by_primary_id(self, primary_id: int) -> Tuple:
        db_session = self.db_session

        sql = "  SELECT COUNT(`register`.id) "
        sql += " FROM " + RegisterGuest.TABLE + " `register` "
        sql += " WHERE 1 = 1 "
        sql += " AND removed = 0 "
        sql += " AND primary_id = " + str(primary_id)
        total_count = db_session.execute(sql).fetchone()[0]

        sql = "  SELECT `register`.* "
        sql += " FROM " + RegisterGuest.TABLE + " `register` "
        sql += " WHERE 1 = 1 "
        sql += " AND removed = 0 "
        sql += " AND primary_id = " + str(primary_id)

        results = db_session.execute(sql)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list

    def find_all_interest(self) -> List[Interest]:
        db_session = self.db_session
        interest_list = db_session.query(Interest).all()
        return interest_list

    def find_interest_list_by_event_id(self, event_id) -> List[Dict]:
        db_session = self.db_session

        sql = '  SELECT interest.* FROM ' + Interest.TABLE + ' AS interest '
        sql += ' LEFT JOIN ' + EventAndInterestRelation.TABLE + ' AS relation ON interest.id = relation.interest_id '
        sql += ' WHERE relation.event_id = :event_id AND relation.removed = 0 '

        results = db_session.execute(sql, {'event_id': event_id})
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return item_list
