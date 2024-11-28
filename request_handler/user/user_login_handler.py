# -*- coding: utf-8 -*-
from flask import Blueprint, request, redirect, make_response, session, json, current_app, jsonify, g
from request_handler.core.core_request_helper import get_real_ip
from request_handler.user.user_request_helper import render_template
from app_model.log_model import LoginHistory
from app_model.user_model import UserStatus
from app_service.user_service import UserService
from app_utility.encrypt_utility import BcryptUtility


user_login_handler = Blueprint('user_login_handler', __name__)


@user_login_handler.route('/', methods=['GET', 'POST'])
@user_login_handler.route('/dashboard/user/', methods=['GET', 'POST'])
@user_login_handler.route('/dashboard/user/login', methods=['GET', 'POST'])
def user_login():
    """ User 登入 """
    db_session = g.db_session
    user_service = UserService(db_session=db_session)
    template_path = 'user/pages/login/login.html'

    if request.method == 'GET':
        return render_template(template_path)
    """ POST """
    history = LoginHistory()
    ip = get_real_ip()

    account = request.form.get('account', '').strip()
    password = request.form.get('password', '').strip()

    if not account or not password:
        return render_template(template_path, message='請輸入帳號密碼')

    user = user_service.find_user_by_account(account=account)
    if not user:
        history.create_user_login_log(user_id=None, user_account=account, ip=ip, result=False)
        db_session.add(history)
        db_session.commit()
        return render_template(template_path, message='帳號或密碼錯誤')

    if user.status == UserStatus.SUSPENDED:
        history.create_user_login_log(user_id=user.id, user_account=account, ip=ip, result=False)
        db_session.add(history)
        db_session.commit()
        return render_template(template_path, header_message='帳號已被停用')

    if not BcryptUtility.verify_password(password, user.password):
        history.create_user_login_log(user_id=user.id, user_account=account, ip=ip, result=False)
        db_session.add(history)
        db_session.commit()
        return render_template(template_path, message='帳號或密碼錯誤')

    history.create_user_login_log(user_id=user.id, user_account=account, ip=ip, result=True)
    db_session.add(history)
    db_session.commit()

    privilege_list = user_service.find_privilege_id_list_by_user_id(user_id=user.id)

    """ 登入成功 """
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_privilege_id_list'] = privilege_list
    return redirect('/dashboard/user/index')


@user_login_handler.route('/dashboard/user/logout', methods=['GET', 'POST'])
def admin_logout():
    """ User 登出 """
    session['user_id'] = None
    session['user_name'] = None
    session['user_privilege_id_list'] = None
    return redirect('/dashboard/user/login')



