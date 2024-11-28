# -*- coding: utf-8 -*-
from typing import Optional
from app_service.core_service import CoreService
from app_model.system_model import MemberCard, RichMenu, MenuType


class MemberCardService(CoreService):

    def find_member_card_by_id(self, member_card_id) -> Optional[MemberCard]:
        db_session = self.db_session
        member_card = db_session.query(MemberCard).filter_by(id=member_card_id).first()
        return member_card

    def find_member_card_by_code(self, code) -> Optional[MemberCard]:
        db_session = self.db_session
        member_card = db_session.query(MemberCard).filter_by(code=code, removed=0).first()
        return member_card

    def find_all_member_card(self):
        """ 搜尋所有 MemberCard """
        db_session = self.db_session
        member_card_list = db_session.query(MemberCard).filter_by(removed=False).all()
        return member_card_list

    def find_member_card_by_criteria(self, criteria: dict, page: int, row_per_page: int):
        db_session = self.db_session
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)

        sql = "  SELECT COUNT(card.id) "
        sql += " FROM " + MemberCard.TABLE + " card "
        sql += " WHERE 1 = 1 "
        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT card.* "
        sql += " FROM " + MemberCard.TABLE + " card "
        sql += " WHERE 1 = 1 "
        sql += " ORDER BY code ASC "
        sql += " LIMIT :index, :count "
        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list


class SystemService(CoreService):

    def find_rich_menu_by_menu_id(self, menu_id) -> Optional[RichMenu]:
        db_session = self.db_session
        rich_menu = db_session.query(RichMenu).filter_by(menu_id=menu_id).first()
        return rich_menu

    def find_active_rich_menu_by_menu_type(self, menu_type) -> Optional[RichMenu]:
        db_session = self.db_session
        rich_menu = db_session.query(RichMenu).filter_by(menu_type=menu_type, removed=0).order_by(RichMenu.id.desc()).first()
        return rich_menu
