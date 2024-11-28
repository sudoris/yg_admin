# -*- coding: utf-8 -*-
from app_config.config import (
    member_liff_channel_id
)
import traceback
from flask import Blueprint, request, redirect, make_response, session, json, current_app, jsonify, abort, g
from app_model.log_model import AppApiLog
from request_handler.core.core_request_helper import get_real_ip
from app_model.member_model import MemberLineInfoAuthToken
from app_utility.line_utility import LineUtility
from app_service.member_service import MemberService


v1_api_member_login_handler = Blueprint('v1_api_member_login_handler', __name__)


@v1_api_member_login_handler.route('/api/v1/member/login', methods=['GET', 'POST'])
def member_login_handler():
    try:
        db_session = g.db_session
        member_service = MemberService(db_session=db_session)

        context = request.json
        current_app.logger.info(context)

        log = AppApiLog(url='/api/v1/member/login', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        id_token = context.get('idToken', '')
        if not id_token:
            payload = {'result': 0, 'message': 'idToken 不得為空'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        line_user_id, email = LineUtility.verify_id_token(id_token, member_liff_channel_id)
        current_app.logger.info('Line User Id: {}'.format(line_user_id))

        line_info = member_service.find_or_create_member_line_info(line_user_id=line_user_id)
        if not line_info.member_id:
            payload = {'result': 0, 'message': '尚未綁定會員'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        auth_token = MemberLineInfoAuthToken(line_info_id=line_info.id)
        db_session.add(auth_token)
        db_session.commit()

        payload = {
            'result': 1,
            'data': {
                'token': auth_token.token
            }
        }
        current_app.logger.info(payload)

        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)

    except Exception as e:
        payload = {'result': 500, 'message': '系統錯誤'}
        current_app.logger.info(traceback.format_exc())
        return jsonify(payload)
