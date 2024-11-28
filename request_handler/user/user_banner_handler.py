# -*- coding: utf-8 -*-
from copy import copy
from datetime import datetime, timedelta
from flask import Blueprint, request, redirect, make_response, session, json, current_app, jsonify, send_file, g
from request_handler.user.user_request_helper import check_user_login, render_template
from app_model.banner_model import Banner
from app_service.banner_service import BannerService
from app_utility.file_utility import save_file


row_per_page = 10
user_banner_handler = Blueprint('user_banner_handler', __name__)


@user_banner_handler.route('/dashboard/user/banner/list', methods=['GET', 'POST'])
@user_banner_handler.route('/dashboard/user/banner/list/<int:page>', methods=['GET', 'POST'])
@check_user_login
def banner_list_handler(user_id, page=1):
    db_session = g.db_session
    service = BannerService(db_session=db_session)

    criteria = {}
    total_count, item_list = service.find_banner_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)

    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    template_path = 'user/pages/banner/banner_list.html'
    return render_template(template_path, item_list=item_list, total_page=total_page, page=page, criteria=criteria)


@user_banner_handler.route('/dashboard/user/banner/create', methods=['GET', 'POST'])
@check_user_login
def banner_create(user_id):
    """ 新增 Banner """
    db_session = g.db_session

    banner = Banner()
    if request.method == 'GET':
        banner.start_date = datetime.now().date()
        template_path = 'user/pages/banner/banner_create.html'
        return render_template(template_path, banner=banner)

    """ POST """
    title = request.values.get('title', '')
    start_date = request.values.get('start_date', '')
    end_date = request.values.get('end_date', '')
    seq = request.values.get('seq', 9999)

    banner.create(title=title, start_date=start_date, end_date=end_date, seq=seq, create_user_id=user_id)

    if 'image' in request.files and request.files['image']:
        upload_file = request.files['image']
        banner.image_url = save_file(upload_file=upload_file, prefix='banner')

    db_session.add(banner)
    db_session.commit()
    return redirect('/dashboard/user/banner/update/{}?result=1&message=新增成功'.format(banner.id))


@user_banner_handler.route('/dashboard/user/banner/update/<int:banner_id>', methods=['GET', 'POST'])
@check_user_login
def banner_update(user_id, banner_id):
    """ 更新 Banner """
    db_session = g.db_session
    service = BannerService(db_session=db_session)

    banner = service.find_banner_by_id(banner_id)
    if not banner or banner.removed:
        return redirect('/dashboard/user/banner/list')

    if request.method == 'GET':
        template_path = 'user/pages/banner/banner_update.html'
        return render_template(template_path, banner=banner)

    """ POST """
    title = request.values.get('title', '')
    start_date = request.values.get('start_date', '')
    end_date = request.values.get('end_date', '')
    seq = request.values.get('seq', 9999)

    banner.update(title=title, start_date=start_date, end_date=end_date, seq=seq, update_user_id=user_id)

    if 'image' in request.files and request.files['image']:
        upload_file = request.files['image']
        banner.image_url = save_file(upload_file=upload_file, prefix='banner')

    db_session.commit()
    return redirect('/dashboard/user/banner/update/{}?result=1&message=更新成功'.format(banner.id))


@user_banner_handler.route('/dashboard/user/banner/delete/<int:banner_id>', methods=['GET', 'POST'])
@user_banner_handler.route('/dashboard/user/banner/delete/<int:banner_id>/<int:page>', methods=['GET', 'POST'])
@check_user_login
def banner_delete(user_id, banner_id, page=1):
    """ 刪除 Banner """
    db_session = g.db_session
    service = BannerService(db_session=db_session)

    banner = service.find_banner_by_id(banner_id)
    if not banner or banner.removed:
        return redirect('/dashboard/user/banner/list')

    banner.delete(update_user_id=user_id)
    db_session.commit()
    return redirect('/dashboard/user/banner/list/{}?result=1&message={}'.format(page, '刪除成功'))

