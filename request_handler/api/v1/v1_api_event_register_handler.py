# -*- coding: utf-8 -*-
import json
import traceback
from request_handler.core.core_request_helper import get_real_ip
from flask import Blueprint, session, request, current_app, jsonify, g
from request_handler.api.api_request_helper import check_line_info_login
from app_model.log_model import AppApiLog
from app_model.event_model import RegisterPrimary, RegisterFamily, RegisterGuest, RegisterStatus
from app_service.event_service import EventService
from app_service.member_service import MemberService


row_per_page = 10
v1_api_event_register_handler = Blueprint('v1_api_event_register_handler', __name__)


@v1_api_event_register_handler.route('/api/v1/event/register/check', methods=['POST'])
@check_line_info_login
def check_register_available(line_info_id, member_id, card_no):
    try:
        db_session = g.db_session
        event_service = EventService(db_session)

        context = request.json
        current_app.logger.info(context)

        log = AppApiLog(url='/api/v1/event/register/check', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        detail_id = context.get('detail_id', '')
        if not detail_id:
            payload = {'result': 0, 'message': '請選擇場次'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        event_detail = event_service.find_event_detail_by_id(detail_id)
        if not event_detail or event_detail.removed:
            payload = {'result': 0, 'message': '場次不存在'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        count = 1
        family_list = context.get('familyList', [])
        guest_list = context.get('guestList', [])
        count += len(family_list)
        count += len(guest_list)

        remain = event_service.calculate_event_detail_remain(detail_id=detail_id)
        if remain < count:
            payload = {'result': 0, 'message': '場次名額不足'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        payload = {
            'result': 1
        }
        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)

    except Exception as e:
        payload = {'result': 0, 'message': '系統錯誤請稍後再試'}
        current_app.logger.info(traceback.format_exc())
        return jsonify(payload)


@v1_api_event_register_handler.route('/api/v1/event/register', methods=['POST'])
@check_line_info_login
def event_register_handler(line_info_id, member_id, card_no):
    try:
        db_session = g.db_session
        event_service = EventService(db_session)
        member_service = MemberService(db_session)

        context = request.json
        current_app.logger.info(context)

        log = AppApiLog(url='/api/v1/event/register', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        detail_id = context.get('detail_id', '')
        payment_1 = context.get('payment1', '')
        payment_2 = context.get('payment2', '')
        payment_3 = context.get('payment3', '')

        if not detail_id:
            payload = {'result': 0, 'message': '請選擇場次'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        event_detail = event_service.find_event_detail_by_id(detail_id)
        if not event_detail or event_detail.removed:
            payload = {'result': 0, 'message': '場次不存在'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        register_primary = event_service.find_register_primary_by_event_detail_id_and_card_no(event_detail_id=detail_id, card_no=card_no)
        if register_primary:
            payload = {'result': 0, 'message': '您已經報名過該場次活動, 請勿重複報名'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        if not payment_1 or not payment_2 or not payment_3:
            payload = {'result': 0, 'message': '請選擇付款順序'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        count = 1
        family_list = context.get('familyList', [])
        guest_list = context.get('guestList', [])

        count += len(family_list)
        count += len(guest_list)

        remain = event_service.calculate_event_detail_remain(detail_id=detail_id)
        status = RegisterStatus.ACCEPT
        if remain < count:
            status = RegisterStatus.WAITING

        primary = RegisterPrimary(event_detail_id=detail_id, line_info_id=line_info_id, member_id=member_id, card_no=card_no, status=status, payment_1=payment_1, payment_2=payment_2, payment_3=payment_3)
        db_session.add(primary)
        db_session.flush()


        for family in family_list:
            name = family.get('name', '').strip()
            card_no = family.get('cardNo', '').strip()
            register_family = RegisterFamily(primary_id=primary.id, name=name, card_no=card_no, status=status)
            db_session.add(register_family)


        for guest in guest_list:
            name = guest.get('name', '').strip()
            register_guest = RegisterGuest(primary_id=primary.id, name=name, status=status)
            db_session.add(register_guest)

        db_session.commit()

        member = member_service.find_member_by_id(member_id)
        interest_list = event_service.find_interest_list_by_event_id(event_detail.primary_id)
        for interest in interest_list:
            interest_id = interest['id']
            if interest_id == 1:
                member.interest_1 += 1
            elif interest_id == 2:
                member.interest_2 += 1
            elif interest_id == 3:
                member.interest_3 += 1
            elif interest_id == 4:
                member.interest_4 += 1
            elif interest_id == 5:
                member.interest_5 += 1
            elif interest_id == 6:
                member.interest_6 += 1
            elif interest_id == 7:
                member.interest_7 += 1
            elif interest_id == 8:
                member.interest_8 += 1
            elif interest_id == 9:
                member.interest_9 += 1
            elif interest_id == 10:
                member.interest_10 += 1
        db_session.commit()

        payload = {
            'result': 1
        }
        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)

    except Exception as e:
        payload = {'result': 0, 'message': '系統錯誤請稍後再試'}
        current_app.logger.info(traceback.format_exc())
        return jsonify(payload)
