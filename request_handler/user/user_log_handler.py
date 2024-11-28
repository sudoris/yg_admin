# -*- coding: utf-8 -*-
import json
import os
from copy import copy
from datetime import datetime, timedelta
from flask import Blueprint, request, current_app, jsonify, redirect, make_response, send_file, g
from request_handler.user.user_request_helper import render_template, check_user_login, check_user_privilege
from app_service.log_service import LogService
from app_utility.string_utility import StringUtility


row_per_page = 10
user_log_handler = Blueprint('user_log_handler', __name__)


@user_log_handler.route('/dashboard/user/log/athena-api', methods=['GET', 'POST'])
@user_log_handler.route('/dashboard/user/log/athena-api/<int:page>', methods=['GET', 'POST'])
@check_user_login
def athena_api_log_list_handler(user_id, page=1):
    db_session = g.db_session
    log_service = LogService(db_session=db_session)

    date_start = request.values.get('date_start', '').strip()
    date_end = request.values.get('date_end', '').strip()
    if not date_start and not date_end:
        now = datetime.now()
        start_datetime = now - timedelta(days=30)
        date_start = start_datetime.strftime('%Y-%m-%d')
        date_end = now.strftime('%Y-%m-%d')

    criteria = {
        'date_start': date_start,
        'date_end': date_end
    }

    total_count, item_list = log_service.find_athena_api_log_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)
    for item in item_list:
        item['result'] = 1 if item['response_body'] else 0

    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    template_path = 'user/pages/log/athena_api.html'
    return render_template(template_path, item_list=item_list, total_page=total_page, page=page, criteria=criteria)


@user_log_handler.route('/dashboard/user/log/app-api', methods=['GET', 'POST'])
@user_log_handler.route('/dashboard/user/log/app-api/<int:page>', methods=['GET', 'POST'])
@check_user_login
def app_api_log_list_handler(user_id, page=1):
    db_session = g.db_session
    log_service = LogService(db_session=db_session)

    date_start = request.values.get('date_start', '').strip()
    date_end = request.values.get('date_end', '').strip()
    if not date_start and not date_end:
        now = datetime.now()
        start_datetime = now - timedelta(days=30)
        date_start = start_datetime.strftime('%Y-%m-%d')
        date_end = now.strftime('%Y-%m-%d')

    criteria = {
        'date_start': date_start,
        'date_end': date_end
    }

    total_count, item_list = log_service.find_app_api_log_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)
    for item in item_list:
        item['result'] = 1
        try:
            json.loads(item['response_body'])
        except Exception as e:
            item['result'] = 0

    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    template_path = 'user/pages/log/app_api.html'
    return render_template(template_path, item_list=item_list, total_page=total_page, page=page, criteria=criteria)


@user_log_handler.route('/dashboard/user/log/sms-history', methods=['GET', 'POST'])
@user_log_handler.route('/dashboard/user/log/sms-history/<int:page>', methods=['GET', 'POST'])
@check_user_login
def sms_history_list_handler(user_id, page=1):
    db_session = g.db_session
    log_service = LogService(db_session=db_session)

    date_start = request.values.get('date_start', '').strip()
    date_end = request.values.get('date_end', '').strip()
    if not date_start and not date_end:
        now = datetime.now()
        start_datetime = now - timedelta(days=30)
        date_start = start_datetime.strftime('%Y-%m-%d')
        date_end = now.strftime('%Y-%m-%d')

    criteria = {
        'mobile': request.values.get('mobile', '').strip(),
        'date_start': date_start,
        'date_end': date_end
    }

    total_count, item_list = log_service.find_sms_history_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)

    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    template_path = 'user/pages/log/sms_history.html'
    return render_template(template_path, item_list=item_list, total_page=total_page, page=page, criteria=criteria)

