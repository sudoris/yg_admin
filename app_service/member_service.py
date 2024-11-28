# -*- coding: utf-8 -*-
from typing import Optional, Tuple, List, Dict, AnyStr
from app_service.core_service import CoreService
from app_model.member_model import MemberTmp, Member, MemberLineInfo, MemberLineInfoAuthToken, MemberMessage


class MemberService(CoreService):

    def find_member_by_id(self, member_id) -> Optional[Member]:
        db_session = self.db_session
        member = db_session.query(Member).filter_by(id=member_id).first()
        return member

    def find_member_by_identify_no(self, identify_no) -> Optional[Member]:
        db_session = self.db_session
        member = db_session.query(Member).filter_by(identify_no=identify_no).first()
        return member

    def find_member_by_criteria(self, criteria: dict, page: int, row_per_page: int) -> Tuple:
        db_session = self.db_session
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)

        if criteria.get('name', None):
            criteria['name'] = "%{}%".format(criteria['name'])
        if criteria.get('identify_no', None):
            criteria['identify_no'] = "%{}%".format(criteria['identify_no'])
        if criteria.get('no', None):
            criteria['no'] = "%{}%".format(criteria['no'])

        sql = "  SELECT COUNT(mem.id) "
        sql += " FROM " + Member.TABLE + " mem "
        sql += " WHERE 1 = 1 "
        if criteria.get('name', None):
            sql += " AND mem.name LIKE :name "
        if criteria.get('identify_no', None):
            sql += " AND mem.identify_no LIKE :identify_no "
        if criteria.get('no', None):
            sql += " AND mem.no LIKE :no "
        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT mem.* "
        sql += " FROM " + Member.TABLE + " mem "
        sql += " WHERE 1 = 1 "
        if criteria.get('name', None):
            sql += " AND mem.name LIKE :name "
        if criteria.get('identify_no', None):
            sql += " AND mem.identify_no LIKE :identify_no "
        if criteria.get('no', None):
            sql += " AND mem.no LIKE :no "
        sql += " ORDER BY id ASC "
        sql += " LIMIT :index, :count "
        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]

        return total_count, item_list

    def find_or_create_member_by_identify_no(self, identify_no, no, name) -> Member:
        db_session = self.db_session
        member = self.find_member_by_identify_no(identify_no=identify_no)
        if member:
            member.no = no
            member.name = name
            db_session.commit()
            return member

        member = Member()
        member.create(identify_no=identify_no)
        member.no = no
        member.name = name
        db_session.add(member)
        db_session.commit()
        return member

    def find_member_line_info_by_criteria(self, criteria, page, row_per_page) -> Tuple:
        db_session = self.db_session
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)

        if criteria.get('display_name', None):
            criteria['display_name'] = "%{}%".format(criteria['display_name'])
        if criteria.get('mobile_opt', None):
            criteria['mobile_opt'] = "%{}%".format(criteria['mobile_opt'])

        flag_member_id = False
        member_id_list = []
        if criteria.get('no', None) or criteria.get('identify_no', None) or criteria.get('member_name', None):
            flag_member_id = True
            if criteria.get('no', None):
                criteria['no'] = "%{}%".format(criteria['no'])
            if criteria.get('identify_no', None):
                criteria['identify_no'] = "%{}%".format(criteria['identify_no'])
            if criteria.get('member_name', None):
                criteria['member_name'] = "%{}%".format(criteria['member_name'])

            sql = "  SELECT * "
            sql += " FROM " + Member.TABLE + " mem "
            sql += " WHERE 1 = 1 "
            if criteria.get('no', None):
                sql += " AND mem.no LIKE :no "
            if criteria.get('identify_no', None):
                sql += " AND mem.identify_no LIKE :identify_no "
            if criteria.get('member_name', None):
                sql += " AND mem.name LIKE :member_name "

            results = db_session.execute(sql, criteria)
            item_list = [dict(zip(row.keys(), row)) for row in results]

            for item in item_list:
                member_id_list.append(item['id'])

            if not item_list:
                return 0, []

        flag_line_user_id = False
        line_user_id_list = []
        if criteria.get('mobile', None):
            flag_line_user_id = True
            if criteria.get('mobile', None):
                criteria['mobile'] = "%{}%".format(criteria['mobile'])
            sql = "  SELECT * "
            sql += " FROM " + MemberTmp.TABLE + " tmp "
            sql += " WHERE 1 = 1 "
            sql += " AND tmp.member_mobile LIKE :mobile "

            results = db_session.execute(sql, criteria)
            item_list = [dict(zip(row.keys(), row)) for row in results]
            for item in item_list:
                line_user_id_list.append(item['line_user_id'])

        sql = "  SELECT COUNT(info.line_user_id) "
        sql += " FROM " + MemberLineInfo.TABLE + " info "
        sql += " WHERE 1 = 1 "
        if criteria.get('display_name', None):
            sql += " AND info.display_name LIKE :display_name "
        if criteria.get('mobile_opt', None):
            sql += " AND info.mobile LIKE :mobile_opt "
        if criteria.get('flag_status', None):
            if criteria['flag_status'] == '1':
                sql += " AND info.member_id IS NOT NULL "
            elif criteria['flag_status'] == '0':
                sql += " AND info.member_id IS NULL "
        if flag_member_id:
            sql += " AND info.member_id IN ( "
            for index, member_id in enumerate(member_id_list):
                sql += "{}".format(member_id)
                if index < len(member_id_list) - 1:
                    sql += ", "
            sql += " ) "
        if flag_line_user_id:
            sql += " AND info.line_user_id IN ( "
            for index, line_user_id in enumerate(line_user_id_list):
                sql += "'{}'".format(line_user_id)
                if index < len(line_user_id_list) - 1:
                    sql += ", "
            sql += " ) "

        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT info.* "
        sql += " FROM " + MemberLineInfo.TABLE + " info "
        sql += " WHERE 1 = 1 "
        if criteria.get('display_name', None):
            sql += " AND info.display_name LIKE :display_name "
        if criteria.get('mobile_opt', None):
            sql += " AND info.mobile LIKE :mobile_opt "
        if criteria.get('flag_status', None):
            if criteria['flag_status'] == '1':
                sql += " AND info.member_id IS NOT NULL "
            elif criteria['flag_status'] == '0':
                sql += " AND info.member_id IS NULL "

        if flag_member_id:
            sql += " AND info.member_id IN ( "
            for index, member_id in enumerate(member_id_list):
                sql += "{}".format(member_id)
                if index < len(member_id_list) - 1:
                    sql += ", "
            sql += " ) "
        if flag_line_user_id:
            sql += " AND info.line_user_id IN ( "
            for index, line_user_id in enumerate(line_user_id_list):
                sql += "'{}'".format(line_user_id)
                if index < len(line_user_id_list) - 1:
                    sql += ", "
            sql += " ) "
        sql += " ORDER BY info.create_datetime DESC "
        sql += " LIMIT :index, :count "

        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list

    def find_last_member_line_info_by_member_id(self, member_id) -> Optional[MemberLineInfo]:
        db_session = self.db_session
        member_line_info = db_session.query(MemberLineInfo).filter_by(member_id=member_id).order_by(MemberLineInfo.update_datetime.desc()).first()
        return member_line_info

    def find_all_member_line_info_by_card_no(self, card_no) -> List[MemberLineInfo]:
        db_session = self.db_session
        member_line_info_list = db_session.query(MemberLineInfo).filter(MemberLineInfo.card_no == card_no, MemberLineInfo.member_id.is_not(None)).all()
        return member_line_info_list

    def find_member_line_info_by_id(self, member_line_info_id) -> Optional[MemberLineInfo]:
        db_session = self.db_session
        line_info = db_session.query(MemberLineInfo).filter_by(id=member_line_info_id).first()
        return line_info

    def find_all_member_line_info_by_member_id(self, member_id) -> List[MemberLineInfo]:
        db_session = self.db_session
        line_info_list = db_session.query(MemberLineInfo).filter_by(member_id=member_id).all()
        return line_info_list

    def find_member_line_info_by_line_user_id(self, line_user_id) -> Optional[MemberLineInfo]:
        db_session = self.db_session
        line_info = db_session.query(MemberLineInfo).filter_by(line_user_id=line_user_id).first()
        return line_info

    def find_or_create_member_line_info(self, line_user_id) -> MemberLineInfo:
        db_session = self.db_session
        member_line_info = self.find_member_line_info_by_line_user_id(line_user_id=line_user_id)
        if member_line_info:
            return member_line_info

        member_line_info = MemberLineInfo()
        member_line_info.create(line_user_id=line_user_id)
        db_session.add(member_line_info)
        db_session.commit()
        return member_line_info

    def find_all_login_line_user_id(self) -> List[AnyStr]:
        db_session = self.db_session
        line_info_list = db_session.query(MemberLineInfo).filter(MemberLineInfo.member_id.is_not(None)).all()
        user_id_list = []
        for line_info in line_info_list:
            user_id_list.append(line_info.line_user_id)
        return user_id_list

    def find_all_unlogin_line_user_id(self) -> List[AnyStr]:
        db_session = self.db_session
        line_info_list = db_session.query(MemberLineInfo).filter(MemberLineInfo.member_id.is_(None)).all()
        user_id_list = []
        for line_info in line_info_list:
            user_id_list.append(line_info.line_user_id)
        return user_id_list

    def find_member_tmp_by_line_user_id(self, line_user_id: str) -> Optional[MemberTmp]:
        db_session = self.db_session
        member_tmp = db_session.query(MemberTmp).filter_by(line_user_id=line_user_id).first()
        return member_tmp

    def find_or_create_member_tmp(self, line_user_id, identify_no, card_no, member_mobile) -> MemberTmp:
        db_session = self.db_session
        member_tmp = self.find_member_tmp_by_line_user_id(line_user_id=line_user_id)
        if member_tmp:
            member_tmp.identify_no = identify_no
            member_tmp.card_no = card_no
            member_tmp.member_mobile = member_mobile
            return member_tmp

        member_tmp = MemberTmp()
        member_tmp.create(line_user_id=line_user_id, identify_no=identify_no, card_no=card_no, member_mobile=member_mobile)
        db_session.add(member_tmp)
        db_session.commit()
        return member_tmp

    def find_member_line_info_auth_token_by_token(self, token) -> Optional[MemberLineInfoAuthToken]:
        db_session = self.db_session
        auth_token = db_session.query(MemberLineInfoAuthToken).filter_by(token=token).first()
        return auth_token

    def find_member_message_by_id(self, message_id) -> Optional[MemberMessage]:
        db_session = self.db_session
        message = db_session.query(MemberMessage).filter_by(id=message_id).first()
        return message

    def find_member_message_by_card_no_list(self, card_no_list, page: int, row_per_page: int) ->Tuple:
        if not card_no_list:
            return 0, 0, []

        criteria = {}
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)

        db_session = self.db_session
        sql = "  SELECT COUNT(id)"
        sql += " FROM " + MemberMessage.TABLE
        sql += " WHERE removed = 0 "
        sql += " AND card_no IN ( "
        for index, card_no in enumerate(card_no_list):
            sql += "'{}'".format(card_no)
            if index < len(card_no_list) - 1:
                sql += ", "
        sql += " ) "
        total_count = db_session.execute(sql, {}).fetchone()[0]

        sql = "  SELECT COUNT(id)"
        sql += " FROM " + MemberMessage.TABLE
        sql += " WHERE removed = 0 AND read_datetime IS NULL "
        sql += " AND card_no IN ( "
        for index, card_no in enumerate(card_no_list):
            sql += "'{}'".format(card_no)
            if index < len(card_no_list) - 1:
                sql += ", "
        sql += " ) "
        total_unread_count = db_session.execute(sql, {}).fetchone()[0]

        sql = "  SELECT id, title, description, create_datetime, read_datetime "
        sql += " FROM " + MemberMessage.TABLE
        sql += " WHERE removed = 0 "
        sql += " AND card_no IN ( "
        for index, card_no in enumerate(card_no_list):
            sql += "'{}'".format(card_no)
            if index < len(card_no_list) - 1:
                sql += ", "
        sql += " ) "
        sql += " ORDER BY create_datetime DESC"
        sql += " LIMIT :index, :count "
        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, total_unread_count, item_list
