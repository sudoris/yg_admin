# -*- coding: utf-8 -*-
import json
from copy import copy
from flask import Blueprint, request, current_app, jsonify, redirect, g
from request_handler.user.user_request_helper import check_user_login, render_template, check_user_privilege
from app_service.user_service import UserService
from app_model.user_model import User, UserStatus, UserAndPrivilegeRelation
from app_model.user_model import privilege_dict


user_account_handler = Blueprint('user_account_handler', __name__)


@user_account_handler.route('/dashboard/user/account/list', methods=['GET', 'POST'])
@user_account_handler.route('/dashboard/user/account/list/<int:page>', methods=['GET', 'POST'])
@check_user_login
def user_account_list(user_id, page=1):
    db_session = g.db_session
    user_service = UserService(db_session=db_session)

    row_per_page = request.values.get('row_per_page', 20)
    criteria = {
        'no': request.values.get('no', ''),
        'name': request.values.get('name', '').strip(),
        'department': request.values.get('department', ''),
        'email': request.values.get('email', '').strip(),
        'status': request.values.get('status', ''),
        'order_by': request.values.get('order_by', ''),
        'sort': request.values.get('sort', 'asc')
    }
    total_count, item_list = user_service.find_user_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)
    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    user_id_list = []
    for item in item_list:
        user_id_list.append(item['id'])

    user_id_and_privilege_id_dict = {}
    relation_list = db_session.query(UserAndPrivilegeRelation).filter(UserAndPrivilegeRelation.user_id.in_(user_id_list), UserAndPrivilegeRelation.removed == 0).all()
    for relation in relation_list:
        privilege_id_list = []
        if relation.user_id in user_id_and_privilege_id_dict:
            privilege_id_list = user_id_and_privilege_id_dict[relation.user_id]

        privilege_id_list.append(relation.privilege_id)
        user_id_and_privilege_id_dict[relation.user_id] = privilege_id_list

    current_app.logger.info(user_id_and_privilege_id_dict)

    for item in item_list:
        privilege = ''
        if item['id'] in user_id_and_privilege_id_dict:
            privilege_id_list = user_id_and_privilege_id_dict[item['id']]
            for index, privilege_id in enumerate(privilege_id_list):
                privilege += privilege_dict[privilege_id]
                if (index + 1) != len(privilege_id_list):
                    privilege += '、'

        item['privilege'] = privilege

    template_path = 'user/pages/account/account_list.html'
    return render_template(template_path, item_list=item_list, UserStatus=UserStatus,
                           row_per_page=row_per_page, page=page, criteria=criteria, total_page=total_page)


@user_account_handler.route('/dashboard/user/account/edit', methods=['GET', 'POST'])
@user_account_handler.route('/dashboard/user/account/edit/<int:edit_user_id>', methods=['GET', 'POST'])
@check_user_login
def user_account_edit(user_id, edit_user_id=None):
    """ 員工基本資料 編輯 """
    db_session = g.db_session
    user_service = UserService(db_session=db_session)
    user_json = {'privilege_list': [], 'department': '', 'status': ''}
    if edit_user_id:
        user = user_service.find_user_by_id(user_id=edit_user_id)
        if not user:
            return redirect('/user/account/list')
        user_json = user.as_dict()
        privilege_list = user_service.find_privilege_id_list_by_user_id(user_id=user.id)
        user_json['privilege_list'] = privilege_list

    template_path = 'user/pages/account/account_edit.html'
    return render_template(template_path, user=json.dumps(user_json, ensure_ascii=False))


@user_account_handler.route('/dashboard/user/account/ajax-save-account', methods=['GET', 'POST'])
@check_user_login
def ajax_save_account(user_id):
    """ Ajax 儲存 User """
    db_session = g.db_session
    user_service = UserService(db_session=db_session)

    context = request.json
    current_app.logger.info(context)

    user_context = context.get('user', {})

    edit_user_id = user_context.get('id', '')
    account = user_context.get('account', '').strip()
    password = user_context.get('password', '').strip()
    name = user_context.get('name', '').strip()
    email = user_context.get('email', '').strip()
    status = user_context.get('status', '').strip()
    privilege_list = user_context.get('privilege_list', [])

    if edit_user_id:
        user = user_service.find_user_by_id(user_id=edit_user_id)
        user.update(name=name, email=email, status=status, editor_user_id=user_id)
        if password:
            user.change_password(password=password)
        db_session.commit()

    else:
        if not account:
            payload = {'result': 0, 'message': '請輸入帳號'}
            current_app.logger.info(payload)
            return jsonify(payload)

        user = user_service.find_user_by_account(account=account)
        if user:
            payload = {'result': 0, 'message': '帳號已經存在'}
            current_app.logger.info(payload)
            return jsonify(payload)

        user = User()
        user.create(account=account, password=password, name=name, email=email, status=status, user_id=user_id)
        db_session.add(user)
        db_session.commit()

    """ 權限 """
    for privilege_id in privilege_list:
        relation = user_service.find_or_create_user_and_privilege_relation(user_id=user.id, privilege_id=privilege_id, create_user_id=user_id)
        relation.update(removed=0, user_id=user_id)
        db_session.commit()

    removed_relation_list = db_session.query(UserAndPrivilegeRelation). \
        filter(UserAndPrivilegeRelation.privilege_id.notin_(privilege_list), UserAndPrivilegeRelation.user_id == user.id,
               UserAndPrivilegeRelation.removed == 0).all()

    for relation in removed_relation_list:
        relation.update(removed=1, user_id=user_id)
        db_session.commit()

    privilege_list = user_service.find_privilege_id_list_by_user_id(user_id=user.id)
    user_payload = user.as_dict()
    user_payload['privilege_list'] = privilege_list

    payload = {
        'result': 1,
        'message': '資料儲存成功',
        'user': user_payload
    }
    current_app.logger.info(payload)
    return jsonify(payload)

