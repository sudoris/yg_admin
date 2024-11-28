# -*- coding: utf-8 -*-
from sqlalchemy import desc
from flask import Blueprint, session, g
from request_handler.user.user_request_helper import check_user_login, render_template
from app_model.log_model import LoginHistory


user_index_handler = Blueprint('user_index_handler', __name__)


@user_index_handler.route('/dashboard/user/index', methods=['GET', 'POST'])
@check_user_login
def user_index(user_id):
    """ 使用者 - 首頁 """
    db_session = g.db_session
    user_history_list = db_session.query(LoginHistory).filter(LoginHistory.user_account.isnot(None)).order_by(desc(LoginHistory.id)).limit(50)
    template_path = 'user/pages/home/index.html'
    return render_template(template_path, user_history_list=user_history_list)
