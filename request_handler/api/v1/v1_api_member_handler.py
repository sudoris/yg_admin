# -*- coding: utf-8 -*-
from app_config.config import (
    domain
)
import traceback
from flask import Blueprint, json, current_app, jsonify, request, g
from request_handler.core.core_request_helper import get_real_ip
from request_handler.api.api_request_helper import check_line_info_login
from app_model.log_model import AppApiLog
from app_service.member_service import MemberService
from app_service.system_service import MemberCardService
from app_utility.athena_utility import query_data_by_card_no, get_member_card_list_by_identify_no


v1_api_member_handler = Blueprint('v1_api_member_handler', __name__)


@v1_api_member_handler.route('/api/v1/member/profile', methods=['GET', 'POST'])
@check_line_info_login
def member_profile_handler(line_info_id, member_id, card_no):
    log = None
    db_session = None
    try:
        db_session = g.db_session
        member_service = MemberService(db_session=db_session)
        member_card_service = MemberCardService(db_session=db_session)

        member = member_service.find_member_by_id(member_id=member_id)

        log = AppApiLog(url='/api/v1/member/profile', request_body=json.dumps({}, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        """ 呼叫德安API查詢 """
        athena_data_context = query_data_by_card_no(card_no=card_no)

        detail_row_context = athena_data_context['ROWSET']['ROW']['DETAIL']['DETAIL_ROW']
        family_row_context = athena_data_context['ROWSET']['ROW']['FAMILY']['FAMILY_ROW'] if athena_data_context['ROWSET']['ROW']['FAMILY'] and 'FAMILY_ROW' in athena_data_context['ROWSET']['ROW']['FAMILY'] else {}

        card_list = []
        is_master = detail_row_context.get('IS_MASTER', '').strip()
        if is_master == 'Y':
            # 主卡
            card_list = get_member_card_list_by_identify_no(member.identify_no)

        name = detail_row_context.get('ALT_NAM', '').strip()
        address = detail_row_context.get('ADDR1_RMK', '').strip()
        mobile = detail_row_context.get('CONTACT_RMK', '').strip()
        identify_no = detail_row_context.get('ID_COD', '').strip().upper()

        member_card_title = detail_row_context.get('MEMBER_NAM', '').strip()
        member_card_code = detail_row_context.get('MEMBER_TYP', '').strip()
        member_card_type = detail_row_context.get('CARD_TYP_NAM', '').strip()
        member_card = member_card_service.find_member_card_by_code(code=member_card_code) # 會員卡
        member_card_payload = {
            'title': member_card_title,
            'cardNo': card_no,
            'imageUrl': domain + member_card.image_url,
            'qrcodeUrl': domain + '/qrcode/' + card_no,
            'barcodeUrl': domain + '/barcode/' + card_no
        }

        flag_add = True
        for card in card_list:
            if card['cardNo'] == card_no:
                flag_add = False
                break
        if flag_add:
            card_list.append({
                'title': member_card_title,
                'cardNo': card_no,
                'cardType': member_card_type
            })

        points = detail_row_context.get('VALID_PTS', 0)
        points_expire_date = detail_row_context.get('EXPIRE_DAT', '')
        balance = detail_row_context.get('BALANCE_AMT', 0)

        family_list_payload = []
        if isinstance(family_row_context, list):
            for family_row in family_row_context:
                family_list_payload.append({
                    'name': family_row.get('ALT_NAM', '').strip(),
                    'cardNo': family_row.get('CARD_NOS', '').strip(),
                    'cardType': family_row.get('CARD_TYP_NAM', '').strip(),
                    'isMaster': family_row.get('IS_MASTER', '').strip()
                })
        elif isinstance(family_row_context, dict):
            if 'CARD_NOS' in family_row_context:
                family_list_payload.append({
                    'name': family_row_context.get('ALT_NAM', '').strip(),
                    'cardNo': family_row_context.get('CARD_NOS', '').strip(),
                    'cardType': family_row_context.get('CARD_TYP_NAM', '').strip(),
                    'isMaster': family_row_context.get('IS_MASTER', '').strip()
                })

        if is_master == 'N':
            """ 因為是附卡, 需要由主卡取得點數跟儲值金 """
            family_master_card_no = ''
            for family in family_list_payload:
                if family['isMaster'] == 'Y':
                    family_master_card_no = family['cardNo']
                    break
            if family_master_card_no:
                master_athena_data_context = query_data_by_card_no(card_no=family_master_card_no)
                family_detail_row_context = master_athena_data_context['ROWSET']['ROW']['DETAIL']['DETAIL_ROW']
                points = family_detail_row_context.get('VALID_PTS', 0)
                points_expire_date = family_detail_row_context.get('EXPIRE_DAT', '')
                balance = family_detail_row_context.get('BALANCE_AMT', 0)

        family_list_payload_pass_exam = []
        if is_master == 'N':
            # 附卡 只能邀請其他主卡
            for family in family_list_payload:
                if family['isMaster'] == 'Y':
                    family_list_payload_pass_exam.append(family)

            family_list_payload = family_list_payload_pass_exam

        gender = 'M'
        if identify_no and len(identify_no) > 2:
            if identify_no[1:2] == '1':
                gender = 'M'
            else:
                gender = 'F'

        data_payload = {
            'name': name,
            'address': address,
            'mobile': mobile,
            'gender': gender,
            'points': points,
            'pointsExpireDate': points_expire_date,
            'balance': balance,
            'card': member_card_payload,
            'cardList': card_list,
            'familyList': family_list_payload
        }

        payload = {
            'result': 1,
            'data': data_payload
        }
        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)

    except Exception as e:
        payload = {'result': 0, 'message': '系統錯誤，系統錯誤請稍後再試'}
        if log and db_session:
            log.response_body = traceback.format_exc()
            db_session.commit()

        current_app.logger.info(traceback.format_exc())
        return jsonify(payload)


@v1_api_member_handler.route('/api/v1/member/change-card-no', methods=['POST'])
@check_line_info_login
def change_card_no_handler(line_info_id, member_id, card_no):
    db_session = g.db_session
    log = None
    try:
        member_service = MemberService(db_session=db_session)

        context = request.json
        current_app.logger.info(context)

        log = AppApiLog(url='/api/v1/member/change-card-no', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        card_no = context.get('cardNo', '').strip()
        if not card_no:
            payload = {'result': 0, 'message': '卡號不可為空'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        line_info = member_service.find_member_line_info_by_id(member_line_info_id=line_info_id)
        line_info.card_no = card_no
        db_session.commit()

        payload = {
            'result': 1
        }
        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)

    except Exception as e:
        payload = {'result': 0, 'message': '系統錯誤'}
        if db_session and log:
            log.response_body = traceback.format_exc()
            db_session.commit()

        current_app.logger.info(traceback.format_exc())
        return jsonify(payload)
