# -*- coding: utf-8 -*-
from app_config.config import (
    domain, member_line_channel_access_token
)
import json
import requests
from io import BytesIO
from flask import Blueprint, request, redirect, make_response, session, json, current_app, jsonify, g
from linebot import LineBotApi
from request_handler.user.user_request_helper import render_template, check_user_login, check_user_privilege
from app_model.system_model import RichMenu, MenuType
from app_service.system_service import SystemService
from app_service.member_service import MemberService
from app_utility.file_utility import save_file


user_rich_menu_handler = Blueprint('user_rich_menu_handler', __name__)


@user_rich_menu_handler.route('/dashboard/user/system/richmenu/<string:menu_type>', methods=['GET', 'POST'])
@check_user_login
def rich_menu_handler(user_id, menu_type):
    """ RichMenu 設定 """
    db_session = g.db_session
    system_servie = SystemService(db_session=db_session)
    member_service = MemberService(db_session=db_session)

    menu_type = menu_type.lower()
    if menu_type not in ['login', 'unlogin']:
        raise Exception('Menu Type Error')

    if menu_type == 'login':
        menu_type_enum = MenuType.LOGIN.name
    else:
        menu_type_enum = MenuType.UNLOGIN.name

    if request.method == 'GET':
        rich_menu = system_servie.find_active_rich_menu_by_menu_type(menu_type=menu_type_enum)
        if not rich_menu:
            rich_menu = RichMenu()

        template_path = 'user/pages/system/rich_menu.html'
        return render_template(template_path, rich_menu=rich_menu, menu_type=menu_type)

    """ POST """
    content = request.values.get('content', '').strip()
    try:
        json_object = json.loads(content)
    except ValueError as e:
        return redirect('/dashboard/user/system/richmenu/{}?result=0&message=請輸入JSON格式設定'.format(menu_type))

    upload_file = request.files.get('menu', None)
    if not upload_file:
        return redirect('/dashboard/user/system/richmenu/{}?result=0&message=請選擇圖片且不超過1mb'.format(menu_type))

    current_app.logger.info('Create RichMenu')
    authorization = 'Bearer {}'.format(member_line_channel_access_token)
    headers = {"Authorization": authorization, "Content-Type": "application/json"}
    response = requests.request('POST', 'https://api.line.me/v2/bot/richmenu', headers=headers, data=content.encode('utf-8'))
    context = json.loads(response.text)
    current_app.logger.info(context)
    menu_id = context['richMenuId']

    url = save_file(upload_file=upload_file, prefix='richmenu')
    menu = RichMenu()
    menu.create(menu_type=menu_type_enum, menu_id=menu_id, content=content, image_url=url, create_user_id=user_id)
    db_session.add(menu)
    db_session.commit()

    line_bot_api = LineBotApi(member_line_channel_access_token)
    upload_file.seek(0)
    line_bot_api.set_rich_menu_image(menu_id, "image/png", upload_file)

    if menu_type == 'unlogin':
        """ 未登入 """
        line_bot_api.set_default_rich_menu(rich_menu_id=menu_id)

    keep_rich_menu_id_list = []
    login_rich_menu = system_servie.find_active_rich_menu_by_menu_type(menu_type=MenuType.LOGIN)
    if login_rich_menu:
        keep_rich_menu_id_list.append(login_rich_menu.menu_id)
    unlogin_rich_menu = system_servie.find_active_rich_menu_by_menu_type(menu_type=MenuType.UNLOGIN)
    if unlogin_rich_menu:
        keep_rich_menu_id_list.append(unlogin_rich_menu.menu_id)

    rich_menu_list = line_bot_api.get_rich_menu_list()
    current_app.logger.info('Total RichMenu Size: {}'.format(len(rich_menu_list)))

    for rich_menu in rich_menu_list:
        current_app.logger.info('Current Check RichMenu: {}'.format(rich_menu.rich_menu_id))
        delete_rich_menu_id = rich_menu.rich_menu_id
        if delete_rich_menu_id not in keep_rich_menu_id_list:
            current_app.logger.info('Delete RichMenu: {}'.format(delete_rich_menu_id))
            line_bot_api.delete_rich_menu(delete_rich_menu_id)
            rich_menu_entity = system_servie.find_rich_menu_by_menu_id(menu_id=delete_rich_menu_id)
            if rich_menu_entity:
                rich_menu_entity.delete(update_user_id=user_id)
                db_session.commit()

    if menu_type == 'unlogin':
        """ 未登入 """
        line_user_id_list = member_service.find_all_unlogin_line_user_id()
    else:
        """ 登入 """
        line_user_id_list = member_service.find_all_login_line_user_id()

    if line_user_id_list:
        total_page, remainder = divmod(len(line_user_id_list), 150)
        if remainder > 0:
            total_page += 1

        for i in range(1, total_page + 1):
            target_line_user_id_list = line_user_id_list[(i - 1) * 150: i * 150]
            current_app.logger.info('link rich menu id: {}, to: {}'.format(menu_id, target_line_user_id_list))
            line_bot_api.link_rich_menu_to_users(user_ids=target_line_user_id_list, rich_menu_id=menu_id)

    return redirect('/dashboard/user/system/richmenu/{}?result=1&message=設定成功'.format(menu_type))
