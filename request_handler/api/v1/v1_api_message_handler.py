# -*- coding: utf-8 -*-
from app_config.config import (
    domain, member_line_channel_access_token
)
import os
import traceback
from datetime import datetime
from linebot import LineBotApi
from linebot.models import TextSendMessage
from jinja2 import Environment, FileSystemLoader
from flask import Blueprint, Response, json, current_app, jsonify, request, g
from request_handler.api.api_request_helper import check_line_info_login
from request_handler.core.core_request_helper import get_real_ip
from app_model.log_model import AppApiLog
from app_model.member_model import MemberMessage
from app_service.member_service import MemberService
from app_utility.athena_utility import query_data_by_card_no, get_member_card_list_by_identify_no
import xmltodict


row_per_page = 10
v1_api_message_handler = Blueprint('v1_api_message_handler', __name__)


@v1_api_message_handler.route('/api/v1/member/message/feed', methods=['GET', 'POST'])
def member_message_feed():
    """ 德安回傳訊息 """
    db_session = None
    log = None
    try:
        db_session = g.db_session
        member_service = MemberService(db_session=db_session)

        data = request.values.get('TxnData', '').strip()
        current_app.logger.info(data)

        log = AppApiLog(url='/api/v1/member/message/feed', request_body=data, ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        if not data:
            xml = """<?xml version="1.0"?>
            <ROWSET>
                <ROW>
            	    <SEND-COD>03009032BO</SEND-COD>
            	    <ACTION_COD>CRM_MSG</ACTION_COD>
            	    <RETN-CODE>0000</RETN-CODE>
            	    <RETN-CODE-DESC>Transaction done successfully.</RETN-CODE-DESC>
            		<MSG-ID>0000</MSG-ID>
            		<MSG-DESC>資料為空</MSG-DESC>
            		<ACTION_DAT>{}</ACTION_DAT>
            	</ROW>
            </ROWSET>""".format(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))

            log.response_body = xml
            db_session.commit()

            response = Response(response=xml, status=200, mimetype="application/xml")
            return response

        context = xmltodict.parse(data)
        current_app.logger.info(context)

        card_no = context['ROWSET']['ROW']['CARD_NOS']
        information = context['ROWSET']['ROW']['INFORMATION_RMK']

        content = [{"content": information, "type": "TEXT"}]
        message = MemberMessage()
        message.create(card_no=card_no, title='儲值金和點數異動', description='', content=json.dumps(content, ensure_ascii=False))
        db_session.add(message)
        db_session.commit()

        xml = """<?xml version="1.0"?>
        <ROWSET>
            <ROW>
                <SEND-COD>03009032BO</SEND-COD>
                <ACTION_COD>CRM_MSG</ACTION_COD>
                <RETN-CODE>0000</RETN-CODE>
                <RETN-CODE-DESC>Transaction done successfully.</RETN-CODE-DESC>
                <MSG-ID>0000</MSG-ID>
                <MSG-DESC>Transaction done successfully.</MSG-DESC>
                <ACTION_DAT>{}</ACTION_DAT>
                </ROW>
        </ROWSET>""".format(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))

        log.response_body = xml
        db_session.commit()

        try:
            line_bot_api = LineBotApi(member_line_channel_access_token)
            send_messages = [TextSendMessage(text=information)]
            member_line_info_list = member_service.find_all_member_line_info_by_card_no(card_no=card_no)
            for member_line_info in member_line_info_list:
                try:
                    line_bot_api.push_message(member_line_info.line_user_id, send_messages)
                except Exception:
                    current_app.logger.error(traceback.format_exc())
        except Exception:
            current_app.logger.error(traceback.format_exc())

        response = Response(response=xml, status=200, mimetype="application/xml")
        return response

    except Exception as e:
        current_app.logger.info(traceback.format_exc())
        if db_session and log:
            log.response_body = traceback.format_exc()
            db_session.commit()

        xml = """<?xml version="1.0"?>
        <ROWSET>
           <ROW>
		     <SEND-COD>03009032BO</SEND-COD>
		     <ACTION_COD>CRM_MSG</ACTION_COD>
		     <RETN-CODE>0000</RETN-CODE>
		     <RETN-CODE-DESC>Transaction done successfully.</RETN-CODE-DESC>
		     <MSG-ID>0000</MSG-ID>
		     <MSG-DESC>系統錯誤</MSG-DESC>
		     <ACTION_DAT>{}</ACTION_DAT>
	       </ROW>
        </ROWSET>""".format(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        response = Response(response=xml, status=200, mimetype="application/xml")
        return response


@v1_api_message_handler.route('/api/v1/member/message/list', methods=['GET', 'POST'])
@check_line_info_login
def message_list_handler(line_info_id, member_id, card_no):
    db_session = None
    log = None
    try:
        db_session = g.db_session
        member_service = MemberService(db_session=db_session)

        page = 1
        if request.method == 'POST':
            context = request.json
            page = context.get('page', 1)
        else:
            context = {}

        log = AppApiLog(url='/api/v1/member/message/list', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        athena_data_context = query_data_by_card_no(card_no=card_no)
        detail_row_context = athena_data_context['ROWSET']['ROW']['DETAIL']['DETAIL_ROW']
        is_master = detail_row_context.get('IS_MASTER', '').strip()

        member = member_service.find_member_by_id(member_id=member_id)

        card_no_list = []
        if is_master == 'Y':
            card_list = get_member_card_list_by_identify_no(member.identify_no)
            for card in card_list:
                card_no_list.append(card['cardNo'])
        else:
            card_no_list.append(card_no)

        total_count, total_unread_count, item_list = member_service.find_member_message_by_card_no_list(card_no_list=card_no_list, page=page, row_per_page=row_per_page)
        total_page, remainder = divmod(total_count, row_per_page)
        if remainder > 0:
            total_page += 1

        for item in item_list:
            item['create_datetime'] = item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S')
            item['flagUnRead'] = 0 if item['read_datetime'] else 1
            del item['read_datetime']

        payload = {
            'result': 1,
            'data': {
                'items': item_list,
                'page': page,
                'totalPage': total_page,
                'totalUnread': total_unread_count
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


@v1_api_message_handler.route('/api/v1/member/message/detail/<int:message_id>', methods=['GET', 'POST'])
@check_line_info_login
def message_detail_handler(line_info_id, member_id, card_no, message_id):
    db_session = None
    log = None
    try:
        db_session = g.db_session
        member_service = MemberService(db_session=db_session)

        log = AppApiLog(url='/api/v1/member/message/detail/' + str(message_id), request_body=json.dumps({}, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        message = member_service.find_member_message_by_id(message_id=message_id)
        if not message or message.removed:
            payload = {'result': 0, 'message': '訊息不存在'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        message.read_datetime = datetime.now()
        db_session.commit()

        env = Environment(loader=FileSystemLoader(searchpath=os.path.join(os.getcwd(), 'template', 'api', 'message')))
        template = env.get_template('content.html')
        content = template.render({'domain': domain, 'content_list': json.loads(message.content)})

        item_payload = {
            'title': message.title,
            'description': message.description,
            'content': content,
            'createDatetime': message.create_datetime.strftime('%Y-%m-%d %H:%M:%S')
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

