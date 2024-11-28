# -*- coding: utf-8 -*-
from copy import copy
from datetime import datetime, timedelta
from flask import Blueprint, request, redirect, make_response, session, json, current_app, jsonify, send_file, g
from request_handler.user.user_request_helper import check_user_login, render_template
from app_model.system_model import MemberCard
from app_service.system_service import MemberCardService
from app_utility.file_utility import save_file


row_per_page = 10
user_member_card_handler = Blueprint('user_member_card_handler', __name__)


@user_member_card_handler.route('/dashboard/user/member-card/list', methods=['GET', 'POST'])
@user_member_card_handler.route('/dashboard/user/member-card/list/<int:page>', methods=['GET', 'POST'])
@check_user_login
def member_card_list_handler(user_id, page=1):
    db_session = g.db_session
    card_service = MemberCardService(db_session=db_session)

    criteria = {}
    total_count, item_list = card_service.find_member_card_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)
    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    template_path = 'user/pages/member_card/member_card_list.html'
    return render_template(template_path, item_list=item_list, total_page=total_page, page=page, criteria=criteria)


@user_member_card_handler.route('/dashboard/user/member-card/create', methods=['GET', 'POST'])
@check_user_login
def member_card_create_handler(user_id):
    db_session = g.db_session

    card = MemberCard()
    if request.method == 'GET':
        template_path = 'user/pages/member_card/member_card_create.html'
        return render_template(template_path, card=card)

    """ POST """
    title = request.values.get('title', '')
    code = request.values.get('code', '')

    card.create(title=title, code=code, create_user_id=user_id)

    if 'image' in request.files and request.files['image']:
        upload_file = request.files['image']
        card.image_url = save_file(upload_file=upload_file, prefix='member_card')

    db_session.add(card)
    db_session.commit()
    return redirect('/dashboard/user/member-card/update/{}?result=1&message=新增成功'.format(card.id))


@user_member_card_handler.route('/dashboard/user/member-card/update/<int:member_card_id>', methods=['GET', 'POST'])
@check_user_login
def member_card_update_handler(user_id, member_card_id):
    db_session = g.db_session
    card_service = MemberCardService(db_session=db_session)

    card = card_service.find_member_card_by_id(member_card_id=member_card_id)
    if not card or card.removed:
        return redirect('/dashboard/user/member-card/list')

    if request.method == 'GET':
        template_path = 'user/pages/member_card/member_card_update.html'
        return render_template(template_path, card=card)

    """ POST """
    title = request.values.get('title', '')
    code = request.values.get('code', '')

    card.update(title=title, code=code, update_user_id=user_id)

    if 'image' in request.files and request.files['image']:
        upload_file = request.files['image']
        card.image_url = save_file(upload_file=upload_file, prefix='member_card')

    db_session.commit()
    return redirect('/dashboard/user/member-card/update/{}?result=1&message=更新成功'.format(card.id))


