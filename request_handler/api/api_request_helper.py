# -*- coding: utf-8 -*-
from functools import wraps
from flask import request, jsonify, current_app, g
from request_handler.core.core_request_helper import get_real_ip
from app_service.member_service import MemberService


def check_line_info_login(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        auth = request.headers.get('auth')
        current_app.logger.info('Auth Token: {} ,From: {} '.format(auth, get_real_ip()))
        if not auth:
            context = {'result': 0, 'code': '403', 'message': 'Empty Auth Token'}
            current_app.logger.info('Empty Auth Token From: {}'.format(get_real_ip()))
            return jsonify(context)

        db_session = g.db_session
        member_service = MemberService(db_session=db_session)
        line_info_auth_token = member_service.find_member_line_info_auth_token_by_token(token=auth)
        if not line_info_auth_token or line_info_auth_token.removed:
            context = {'result': 0, 'code': '403', 'message': 'Invalid Auth Token'}
            current_app.logger.info('Invalid Auth Token From: {} , With: {}'.format(get_real_ip(), auth))
            return jsonify(context)

        line_info = member_service.find_member_line_info_by_id(member_line_info_id=line_info_auth_token.line_info_id)
        if not line_info.member_id:
            context = {'result': 0, 'code': '403', 'message': 'Line 使用者尚未綁定'}
            current_app.logger.info('Invalid Auth Token From: {} , With: {}'.format(get_real_ip(), auth))
            return jsonify(context)

        return func(line_info_id=line_info_auth_token.line_info_id, member_id=line_info.member_id, card_no=line_info.card_no, *args, **kwargs)

    return wrapped
