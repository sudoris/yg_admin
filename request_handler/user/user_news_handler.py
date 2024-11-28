# -*- coding: utf-8 -*-
from copy import copy
from datetime import datetime
from flask import Blueprint, request, redirect, make_response, session, json, current_app, jsonify, g
from request_handler.user.user_request_helper import render_template, check_user_login, check_user_privilege
from app_model.news_model import News
from app_service.news_service import NewsService
from app_utility.file_utility import save_base64_str, save_file


row_per_page = 10
user_news_handler = Blueprint('user_news_handler', __name__)


@user_news_handler.route('/dashboard/user/news/list', methods=['GET', 'POST'])
@user_news_handler.route('/dashboard/user/news/list/<int:page>', methods=['GET', 'POST'])
@check_user_login
def news_list_handler(user_id, page=1):
    """ News 列表 """
    db_session = g.db_session
    media_service = NewsService(db_session=db_session)
    template_path = 'user/pages/news/news_list.html'

    criteria = {
        'title': request.values.get('title', '').strip(),
        'status': request.values.get('status', '')
    }

    total_count, item_list = media_service.find_news_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)

    news_id_list = []
    for item in item_list:
        news_id_list.append(item['id'])

    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    return render_template(template_path, item_list=item_list, total_page=total_page, page=page, criteria=criteria)


@user_news_handler.route('/dashboard/user/news/create', methods=['GET', 'POST'])
@check_user_login
def news_create_handler(user_id):
    """ 新增 News """
    db_session = g.db_session
    service = NewsService(db_session=db_session)

    template_path = 'user/pages/news/news_create.html'
    news = News()

    if request.method == 'GET':
        content = news.content if news.content else '[]'
        return render_template(template_path, news=news, today=datetime.now().strftime('%Y-%m-%d'),
                               fragmentList=json.dumps(content, ensure_ascii=False))

    """ POST """
    title = request.values.get('title', '')
    description = request.values.get('description', '')
    status = request.values.get('status', '')
    flag_top = request.values.get('flag_top', 0)
    display_date = request.values.get('display_date', '')
    line_keyword = request.values.get('line_keyword', '')
    flag_visitor = request.values.get('flag_visitor', 0)
    flag_member = request.values.get('flag_member', 0)

    content = request.values.get('content')
    context = json.loads(content)
    for item in context:
        if item['content'].startswith('data:'):
            item['content'] = save_base64_str(item['content'], 'news')

    news.create(title=title, description=description, content=json.dumps(context), status=status, flag_top=flag_top, display_date=display_date,
                flag_visitor=flag_visitor, flag_member=flag_member, line_keyword=line_keyword, create_user_id=user_id)

    db_session.add(news)
    db_session.commit()

    if 'cover_image' in request.files and request.files['cover_image']:
        upload_file = request.files['cover_image']
        news.cover_image = save_file(upload_file=upload_file, prefix='news')
        db_session.commit()

    return redirect('/dashboard/user/news/update/{}?result=1&message={}'.format(news.id, '新增成功'))


@user_news_handler.route('/dashboard/user/news/update/<int:news_id>', methods=['GET', 'POST'])
@check_user_login
def news_update_handler(user_id, news_id):
    db_session = g.db_session
    news_service = NewsService(db_session=db_session)
    template_path = 'user/pages/news/news_update.html'

    news = news_service.find_news_by_id(news_id)
    if not news or news.removed:
        return redirect('/dashboard/user/news/list')

    if request.method == 'GET':
        content = news.content if news.content else '[]'
        return render_template(template_path, news=news, today=datetime.now().strftime('%Y-%m-%d'),
                               fragmentList=json.dumps(content, ensure_ascii=False))

    """ POST """
    title = request.values.get('title', '')
    description = request.values.get('description', '')
    status = request.values.get('status', '')
    flag_top = request.values.get('flag_top', 0)
    display_date = request.values.get('display_date', '')
    flag_visitor = request.values.get('flag_visitor', 0)
    flag_member = request.values.get('flag_member', 0)
    line_keyword = request.values.get('line_keyword', '')

    content = request.values.get('content')
    context = json.loads(content)
    for item in context:
        if item['content'].startswith('data:'):
            item['content'] = save_base64_str(item['content'], 'news')

    news.update(title=title, description=description, content=json.dumps(context), status=status, flag_top=flag_top, display_date=display_date,
                line_keyword=line_keyword, flag_visitor=flag_visitor, flag_member=flag_member, update_user_id=user_id)
    db_session.commit()

    if 'cover_image' in request.files and request.files['cover_image']:
        upload_file = request.files['cover_image']
        news.cover_image = save_file(upload_file=upload_file, prefix='news')
        db_session.commit()

    return redirect('/dashboard/user/news/update/{}?result=1&message={}'.format(news.id, '更新成功'))


@user_news_handler.route('/dashboard/user/news/delete/<int:news_id>', methods=['GET', 'POST'])
@user_news_handler.route('/dashboard/user/news/delete/<int:news_id>/<int:page>', methods=['GET', 'POST'])
@check_user_login
def news_delete_handler(user_id, news_id, page=1):
    """ 刪除 News """
    db_session = g.db_session
    news_service = NewsService(db_session=db_session)

    news = news_service.find_news_by_id(news_id)
    if not news or news.removed:
        return redirect('/dashboard/user/news/list/{}'.format(page))

    news.delete(update_user_id=user_id)
    db_session.commit()
    return redirect('/dashboard/user/news/list/{}?result=1&message={}'.format(page, '刪除成功'))

