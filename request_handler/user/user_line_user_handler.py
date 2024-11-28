# -*- coding: utf-8 -*-
from app_config.config import (
    member_line_channel_access_token
)
import traceback
from copy import copy
from datetime import datetime, timedelta
from flask import Blueprint, request, redirect, make_response, session, json, current_app, jsonify, g
from linebot import LineBotApi
from request_handler.user.user_request_helper import render_template, check_user_login
from app_model.system_model import MenuType
from app_service.member_service import MemberService
from app_service.system_service import SystemService


row_per_page = 10
user_line_user_handler = Blueprint('user_line_user_handler', __name__)


@user_line_user_handler.route('/dashboard/user/line-user/list', methods=['GET', 'POST'])
@user_line_user_handler.route('/dashboard/user/line-user/list/<int:page>', methods=['GET', 'POST'])
@check_user_login
def line_user_list_handler(user_id, page=1):
    """ Line User 列表 """
    db_session = g.db_session
    member_service = MemberService(db_session=db_session)

    expire = datetime.now() - timedelta(days=1)
    criteria = {
        'no': request.values.get('no', '').strip(),
        'identify_no': request.values.get('identify_no', '').strip(),
        'display_name': request.values.get('display_name', '').strip(),
        'member_name': request.values.get('member_name', '').strip(),
        'mobile': request.values.get('mobile', '').strip(),
        'mobile_opt': request.values.get('mobile_opt', '').strip(),
        'flag_status': request.values.get('flag_status', '').strip()
    }
    total_count, line_info_list = member_service.find_member_line_info_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)
    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    line_bot_api = LineBotApi(member_line_channel_access_token)

    for line_info in line_info_list:
        member_line_info = member_service.find_member_line_info_by_id(line_info['id'])
        member_tmp = member_service.find_member_tmp_by_line_user_id(line_info['line_user_id'])
        if member_line_info.member_id:
            member = member_service.find_member_by_id(member_line_info.member_id)
            line_info['identify_no'] = member.identify_no
            line_info['member_name'] = member.name

        line_info['member_mobile'] = member_tmp.member_mobile
        if not member_line_info.mobile:
            line_info['mobile'] = member_tmp.mobile

        if not line_info['display_name']:
            try:
                profile = line_bot_api.get_profile(user_id=line_info['line_user_id'])
                line_info['display_name'] = profile.display_name
                member_line_info.display_name = profile.display_name

                line_info['picture_url'] = profile.picture_url
                member_line_info.picture_url = profile.picture_url
                member_line_info.update_datetime = datetime.now()

                db_session.commit()
            except Exception:
                current_app.logger.error(traceback.format_exc())

    template_path = 'user/pages/line_user/line_user_list.html'
    return render_template(template_path, item_list=line_info_list, total_page=total_page, page=page, row_per_page=row_per_page, criteria=criteria)


@user_line_user_handler.route('/dashboard/user/line-user/reject/<string:line_user_id>/<int:page>', methods=['GET', 'POST'])
@check_user_login
def line_user_reject_handler(user_id, line_user_id, page=1):
    """ Line 使用者 拒絕認證 """
    db_session = g.db_session
    member_service = MemberService(db_session=db_session)
    system_service = SystemService(db_session=db_session)

    member_line_info = member_service.find_member_line_info_by_line_user_id(line_user_id=line_user_id)
    if not member_line_info:
        return redirect('/dashboard/user/line-user/list')

    member_line_info.member_id = None
    member_line_info.card_no = ''
    member_line_info.mobile = ''
    member_line_info.status = 0
    db_session.commit()

    rich_menu = system_service.find_active_rich_menu_by_menu_type(MenuType.UNLOGIN)
    line_bot_api = LineBotApi(member_line_channel_access_token)
    line_bot_api.link_rich_menu_to_user(line_user_id, rich_menu.menu_id)
    return redirect('/dashboard/user/line-user/list/{}'.format(page))
