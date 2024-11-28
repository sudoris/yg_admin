# -*- coding: utf-8 -*-
from app_config.config import (
    athena_api_url
)
import requests
import xmltodict
from datetime import datetime
from urllib.parse import quote
from flask import current_app, g
from app_model.log_model import AthenaApiLog


def query_data_by_card_no(card_no):
    """ 使用會員卡號查詢 """
    db_session = g.db_session
    action_datetime = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    xml = """<?xml version="1.0"?>
            <ROWSET>
                <ROW>
    	            <REVE-CODE>0300BO3290</REVE-CODE>
    	            <ACTION_COD>CRM_QRY_ARGO</ACTION_COD>
    	            <CARD_NOS>{}</CARD_NOS>
    	            <ACTION_DAT>{}</ACTION_DAT>
    	        </ROW>
    	    </ROWSET>""".format(card_no, action_datetime)
    url = athena_api_url + '?TxnData=' + quote(xml).replace('/', '%2F')

    current_app.logger.info(xml)
    current_app.logger.info(url)

    log = AthenaApiLog(url=athena_api_url, request_body=xml)
    db_session.add(log)
    db_session.commit()

    response = requests.get(url)
    response_body = response.text

    log.response_body = response_body
    db_session.commit()

    return xmltodict.parse(response_body)

def query_data_by_identify_no(identify_no):
    """ 使用身分證查詢 """
    db_session = g.db_session
    action_datetime = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    xml = """<?xml version="1.0"?>
                <ROWSET>
        	        <ROW>
        		        <REVE-CODE>0300BO3290</REVE-CODE>
        		    <ACTION_COD>CRM_IDQRY_ARGO</ACTION_COD>
        		<ID_COD>{}</ID_COD>
        		<ACTION_DAT>{}</ACTION_DAT>
        	</ROW>
        </ROWSET>""".format(identify_no, action_datetime)

    url = athena_api_url + '?TxnData=' + quote(xml).replace('/', '%2F')

    log = AthenaApiLog(url=athena_api_url, request_body=xml)
    db_session.add(log)
    db_session.commit()

    response = requests.get(url)
    response_body = response.text

    log.response_body = response_body
    db_session.commit()

    return xmltodict.parse(response_body)


def get_member_card_list_by_identify_no(identify_no):
    payload = []
    athena_context = query_data_by_identify_no(identify_no=identify_no)
    detail_row_context = athena_context['ROWSET']['ROW']['DETAIL']['DETAIL_ROW'] if athena_context['ROWSET']['ROW']['DETAIL'] and 'DETAIL_ROW' in athena_context['ROWSET']['ROW']['DETAIL'] else {}
    if isinstance(detail_row_context, list):
        for detail in detail_row_context:
            payload.append({
                'title': detail.get('MEMBER_NAM', '').strip(),
                'cardNo': detail.get('CARD_NOS', '').strip(),
                'cardType': detail.get('CARD_TYP_NAM', '').strip()
            })
    elif isinstance(detail_row_context, dict):
        payload.append({
            'title': detail_row_context.get('MEMBER_NAM', '').strip(),
            'cardNo': detail_row_context.get('CARD_NOS', '').strip(),
            'cardType': detail_row_context.get('CARD_TYP_NAM', '').strip()
        })
    return payload
