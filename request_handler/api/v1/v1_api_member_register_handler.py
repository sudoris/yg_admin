# -*- coding: utf-8 -*-
from app_config.config import (
    member_liff_channel_id, member_line_channel_access_token, sms_uid, sms_pwd
)
import requests
import traceback
from datetime import datetime, timedelta
from linebot import LineBotApi
from flask import Blueprint, request, redirect, make_response, session, json, current_app, jsonify, abort, g
from app_model.log_model import AppApiLog, SMSHistory
from request_handler.core.core_request_helper import get_real_ip
from app_model.system_model import MenuType
from app_service.log_service import LogService
from app_service.member_service import MemberService
from app_service.system_service import SystemService
from app_utility.athena_utility import query_data_by_card_no
from app_utility.string_utility import StringUtility
from app_utility.line_utility import LineUtility


v1_api_member_register_handler = Blueprint('v1_api_member_register_handler', __name__)


@v1_api_member_register_handler.route('/api/v1/member/register/step-1', methods=['GET', 'POST'])
def member_register_step_1():
    """ 會員註冊 Step-1 """
    try:
        db_session = g.db_session
        member_service = MemberService(db_session=db_session)

        context = request.json
        current_app.logger.info(context)

        log = AppApiLog(url='/api/v1/member/register/step-1', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
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

        identify_no = context.get('identifyNo', '').strip().upper()
        card_no = context.get('cardNo', '').strip().upper()
        member_mobile = context.get('memberMobile', '').replace('-', '').replace('–', '').strip()

        if not identify_no:
            payload = {'result': 0, 'message': '請輸入會員身分證字號'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        if not card_no:
            payload = {'result': 0, 'message': '請輸入會員代號'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        if not member_mobile:
            payload = {'result': 0, 'message': '請輸入會員手機號碼'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        """ 呼叫德安API查詢 """
        athena_data_context = query_data_by_card_no(card_no=card_no)
        current_app.logger.info(json.dumps(athena_data_context, ensure_ascii=False))

        if 'ROWSET' not in athena_data_context:
            payload = {'result': 0, 'message': '查無此會員資料'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        rowset_context = athena_data_context['ROWSET']
        if 'ROW' not in rowset_context:
            payload = {'result': 0, 'message': '查無此會員資料'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        row_context = rowset_context['ROW']
        if 'DETAIL' not in row_context:
            payload = {'result': 0, 'message': '查無此會員資料'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        detail_context = row_context['DETAIL']
        if 'DETAIL_ROW' not in detail_context:
            payload = {'result': 0, 'message': '查無此會員資料'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        detail_row_context = detail_context['DETAIL_ROW']
        test_identify_no = detail_row_context.get('ID_COD', '').strip().upper()
        if identify_no != test_identify_no:
            payload = {'result': 0, 'message': '身分證號碼不符合'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        is_master = detail_row_context.get('IS_MASTER', 'N').strip()
        no = detail_row_context.get('MEMBER_COD', '').strip()
        name = detail_row_context.get('ALT_NAM', '').strip()

        test_mobile = detail_row_context.get('CONTACT_RMK', '').replace('-', '').replace('–', '').strip()
        test_mobile_2 = detail_row_context.get('ATTEN_PHONE', '').replace('-', '').replace('–', '').strip()  # 第一聯絡人/秘書 電話

        current_app.logger.info('會員手機號碼: {}'.format(test_mobile))
        current_app.logger.info('秘書電話: {}'.format(test_mobile_2))

        if member_mobile != test_mobile and member_mobile != test_mobile_2:
            payload = {'result': 0, 'message': '手機號碼不符合'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        member = member_service.find_or_create_member_by_identify_no(identify_no=identify_no, no=no, name=name)

        flag_amount_limit_pass = True
        registered_member_line_info_list = member_service.find_all_member_line_info_by_member_id(member_id=member.id)
        if is_master == 'Y':
            if len(registered_member_line_info_list) >= 2:
                flag_amount_limit_pass = False
        else:
            if len(registered_member_line_info_list) >= 1:
                flag_amount_limit_pass = False

        if not flag_amount_limit_pass:
            payload = {'result': 0, 'message': '此會籍編號已有認證，若有任何疑問請洽專屬祕書或業務'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        """ 資料正確, 存入 MemberTmp """
        member_tmp = member_service.find_or_create_member_tmp(line_user_id=line_user_id, identify_no=identify_no, card_no=card_no, member_mobile=member_mobile)
        member_line_info = member_service.find_or_create_member_line_info(line_user_id=line_user_id)

        payload = {'result': 1}
        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)

    except Exception as e:
        payload = {'result': 0, 'message': '系統錯誤請稍後再試'}
        current_app.logger.info(traceback.format_exc())
        return jsonify(payload)


@v1_api_member_register_handler.route('/api/v1/member/register/step-2', methods=['GET', 'POST'])
def member_register_step_2():
    """ 輸入當前使用者的手機號碼, 並發送簡訊 """
    try:
        db_session = g.db_session
        member_service = MemberService(db_session=db_session)

        context = request.json
        current_app.logger.info(context)

        log = AppApiLog(url='/api/v1/member/register/step-2', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
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

        identify_no = context.get('identifyNo', '').strip().upper()
        card_no = context.get('cardNo', '').strip().upper()
        member_mobile = context.get('memberMobile', '').strip()
        mobile = context.get('mobile', '').replace('-', '').replace('–', '').strip()

        member_tmp = member_service.find_member_tmp_by_line_user_id(line_user_id=line_user_id)
        if not member_tmp.identify_no:
            payload = {'result': 0, 'message': '錯誤的驗證流程'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        if not StringUtility.verify_mobile(mobile):
            payload = {'result': 0, 'message': '手機號碼錯誤'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        """ 發送簡訊 """
        member_tmp.mobile = mobile
        member_tmp.code = StringUtility.generate_random_number(6)
        db_session.commit()

        params = {'UID': sms_uid, 'PWD': sms_pwd, 'SB': '亞果遊艇會'}
        message = '歡迎加入亞果遊艇會會員中心，您的驗證碼為 {} ，請於10分鐘內輸入驗證碼完成驗證。'.format(member_tmp.code)
        params['MSG'] = message
        params['DEST'] = mobile

        sms_url = 'https://oms.every8d.com/API21/HTTP/sendSMS.ashx'
        response = requests.get(url=sms_url, params=params)
        current_app.logger.info(response.text)

        sms_history = SMSHistory(mobile=mobile, content=message)
        db_session.add(sms_history)
        db_session.commit()

        payload = {'result': 1}
        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)

    except Exception as e:
        payload = {'result': 0, 'message': '系統錯誤請稍後再試'}
        current_app.logger.info(traceback.format_exc())
        return jsonify(payload)

@v1_api_member_register_handler.route('/api/v1/member/register/step-3', methods=['GET', 'POST'])
def member_register_step_3():
    try:
        db_session = g.db_session
        member_service = MemberService(db_session=db_session)
        system_service = SystemService(db_session=db_session)

        context = request.json
        current_app.logger.info(context)

        log = AppApiLog(url='/api/v1/member/register/step-3', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
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

        identify_no = context.get('identifyNo', '').strip().upper()
        card_no = context.get('cardNo', '').strip().upper()
        member_mobile = context.get('memberMobile', '').strip()
        mobile = context.get('mobile', '').strip()
        code = context.get('code', '').strip()

        member_tmp = member_service.find_member_tmp_by_line_user_id(line_user_id=line_user_id)
        if not member_tmp.identify_no:
            payload = {'result': 0, 'message': '錯誤的驗證流程'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        if code != member_tmp.code:
            payload = {'result': 0, 'message': '驗證碼錯誤'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        """ 成功 """
        member = member_service.find_member_by_identify_no(identify_no=member_tmp.identify_no)

        member_line_info = member_service.find_or_create_member_line_info(line_user_id=line_user_id)
        member_line_info.member_id = member.id
        member_line_info.card_no = member_tmp.card_no
        member_line_info.mobile = member_tmp.mobile
        db_session.commit()

        line_bot_api = LineBotApi(member_line_channel_access_token)
        rich_menu = system_service.find_active_rich_menu_by_menu_type(menu_type=MenuType.LOGIN)
        if rich_menu:
            current_app.logger.info('Link Rich Menu: {} to User: {}'.format(rich_menu.menu_id, line_user_id))
            line_bot_api.link_rich_menu_to_user(user_id=line_user_id, rich_menu_id=rich_menu.menu_id)

        payload = {'result': 1}
        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)

    except Exception as e:
        payload = {'result': 0, 'message': '系統錯誤請稍後再試'}
        current_app.logger.info(traceback.format_exc())
        return jsonify(payload)
