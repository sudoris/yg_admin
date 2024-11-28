# -*- coding: utf-8 -*-
from typing import Optional, Tuple, List, Dict
from app_service.core_service import CoreService
from app_model.user_model import User, UserAndPrivilegeRelation


class UserService(CoreService):

    def find_user_by_id(self, user_id) -> Optional[User]:
        db_session = self.db_session
        user = db_session.query(User).filter_by(id=user_id).first()
        return user

    def find_user_by_account(self, account) -> Optional[User]:
        db_session = self.db_session
        user = db_session.query(User).filter_by(account=account).first()
        return user

    def find_user_by_criteria(self, criteria: dict, page: int, row_per_page: int) -> Tuple:
        db_session = self.db_session
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)
        if criteria.get('name', None):
            criteria['name'] = '%' + criteria['name'] + '%'
        if criteria.get('email', None):
            criteria['email'] = '%' + criteria['email'] + '%'

        sql = "  SELECT COUNT(user.id) "
        sql += " FROM " + User.TABLE + " user "
        sql += " WHERE 1 = 1 "
        if criteria.get('name', None):
            sql += " AND user.name LIKE :name "
        if criteria.get('email', None):
            sql += " AND user.email LIKE :email "
        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT user.id, user.account, user.status, user.email, user.name "
        sql += " FROM " + User.TABLE + " user "
        sql += " WHERE 1 = 1 "
        if criteria.get('name', None):
            sql += " AND user.name LIKE :name "
        if criteria.get('email', None):
            sql += " AND user.email LIKE :email "
        sql += " ORDER BY user.id ASC "
        sql += " LIMIT :index, :count "

        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list

    def find_or_create_user_and_privilege_relation(self, user_id, privilege_id, create_user_id) -> Optional[UserAndPrivilegeRelation]:
        """ 查詢 或建立 UserAndPrivilegeRelation """
        db_session = self.db_session
        relation = db_session.query(UserAndPrivilegeRelation).filter_by(user_id=user_id, privilege_id=privilege_id).first()
        if relation:
            return relation

        relation = UserAndPrivilegeRelation(user_id=user_id, privilege_id=privilege_id, create_user_id=create_user_id)
        db_session.add(relation)
        db_session.commit()
        return relation

    def find_privilege_id_list_by_user_id(self, user_id):
        db_session = self.db_session
        relation_list = db_session.query(UserAndPrivilegeRelation).filter_by(user_id=user_id, removed=0).all()

        privilege_id_list = []
        for relation in relation_list:
            privilege_id_list.append(relation.privilege_id)

        return privilege_id_list


