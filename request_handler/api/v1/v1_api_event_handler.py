# -*- coding: utf-8 -*-
from app_config.config import (
    domain
)
import json
import traceback
from copy import copy
from datetime import datetime, time
from request_handler.core.core_request_helper import get_real_ip
from request_handler.api.api_request_helper import check_line_info_login
from flask import Blueprint, session, request, current_app, jsonify, g
from app_model.log_model import AppApiLog
from app_service.event_service import EventService
from app_model.event_model import EventStatus


row_per_page = 10
v1_api_event_handler = Blueprint('v1_api_event_handler', __name__)


@v1_api_event_handler.route('/api/v1/event/list', methods=['GET', 'POST'])
@check_line_info_login
def event_list(line_info_id, member_id, card_no):
    db_session = None
    log = None
    try:
        db_session = g.db_session
        event_service = EventService(db_session=db_session)

        page = 1
        if request.method == 'POST':
            context = request.json
            page = context.get('page', 1)
        else:
            context = {}

        log = AppApiLog(url='/api/v1/event/list', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        criteria = {
            'status': 'NORMAL'
        }
        total_count, item_list = event_service.api_find_event_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)

        total_page, remainder = divmod(total_count, row_per_page)
        if remainder > 0:
            total_page += 1

        items_payload = []
        for item in item_list:
            items_payload.append({
                'id': item['id'],
                'title': item['title'],
                'description': item['description'],
                'startDate': item['start_date'].strftime('%Y-%m-%d'),
                'endDate': item['end_date'].strftime('%Y-%m-%d'),
                'images': [domain + item['cover_image']]
            })

        payload = {
            'result': 1,
            'data': {
                'items': items_payload,
                'totalPage': total_page,
                'page': page
            }
        }

        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)
    except Exception as e:
        current_app.logger.info(traceback.format_exc())
        if db_session and log:
            log.response_body = traceback.format_exc()
            db_session.commit()

        payload = {'result': 0, 'message': '系統錯誤請稍後再試'}
        return jsonify(payload)


@v1_api_event_handler.route('/api/v1/event/detail/<int:event_id>', methods=['GET', 'POST'])
@check_line_info_login
def event_detail(line_info_id, member_id, card_no, event_id):
    db_session = None
    log = None
    try:
        db_session = g.db_session
        event_service = EventService(db_session=db_session)

        log = AppApiLog(url='/api/v1/event/detail/' + str(event_id), request_body=json.dumps({}, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        event_primary = event_service.find_event_primary_by_id(primary_id=event_id)
        if not event_primary or event_primary.removed or event_primary.status != EventStatus.NORMAL:
            payload = {'result': 0, 'message': '活動不存在'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        now = datetime.now()
        detail_payload = []
        detail_list = event_service.find_all_event_detail_by_primary_id(primary_id=event_id)
        for detail in detail_list:
            end_date = datetime.combine(detail.end_date, time(hour=23, minute=59, second=59, microsecond=0))
            if end_date > now:
                detail_payload.append({
                    'detail_id': detail.id,
                    'location': detail.location,
                    'time': detail.time,
                    'limit': detail.limit
                })

        now = datetime.now()
        start_datetime = datetime.combine(event_primary.start_date, time=time(hour=0, minute=0, second=0, microsecond=0))
        end_datetime = datetime.combine(event_primary.end_date, time=time(hour=23, minute=59, second=59, microsecond=0))
        flag_register = 1 if start_datetime <= now <= end_datetime else 0

        item_payload = {
            'id': event_primary.id,
            'title': event_primary.title,
            'description': event_primary.description,
            'images': [domain + event_primary.cover_image],
            'startDate': event_primary.start_date.strftime('%Y-%m-%d'),
            'endDate': event_primary.end_date.strftime('%Y-%m-%d'),
            'flagRegister': flag_register,
            'content': '<style>p{margin-top:0px; margin-bottom:0px}</style><div>' + event_primary.content.replace('\r', '').replace('\n', '') + '</div>',
            'contentFee': '<style>p{margin-top:0px; margin-bottom:0px}</style><div>' + event_primary.content_fee.replace('\r', '').replace('\n', '') + '</div>',
            'contentRefund': '<style>p{margin-top:0px; margin-bottom:0px}</style><div>' + event_primary.content_refund.replace('\r', '').replace('\n', '') + '</div>',
            'detailList': detail_payload
        }
        payload = {
            'result': 1,
            'data': {
                'item': item_payload
            }
        }
        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)

    except Exception as e:
        current_app.logger.info(traceback.format_exc())
        if db_session and log:
            log.response_body = traceback.format_exc()
            db_session.commit()
        payload = {'result': 0, 'message': '系統錯誤請稍後再試'}
        return jsonify(payload)

