# -*- coding: utf-8 -*-
from app_config.config import (
    domain
)
import os
import json
import traceback
from copy import copy
from flask import Blueprint, request, current_app, jsonify, g
from jinja2 import Environment, FileSystemLoader
from request_handler.core.core_request_helper import get_real_ip
from app_model.log_model import AppApiLog
from app_service.product_service import ProductService
from app_model.product_model import ProductStatus


v1_api_product_handler = Blueprint('v1_api_product_handler', __name__)


@v1_api_product_handler.route('/api/v1/product/colors', methods=['GET', 'POST'])
def product_color_handler():
    try:
        db_session = g.db_session
        product_service = ProductService(db_session=db_session)

        product_color_list = product_service.find_all_product_color()
        data = {}
        for product_color in product_color_list:
            data[product_color.title] = product_color.code

        payload = {'result': 1, 'data': data}
        return jsonify(payload)
    except Exception as e:
        payload = {'result': 500, 'message': '系統錯誤'}
        current_app.logger.info(traceback.format_exc())
        return jsonify(payload)


@v1_api_product_handler.route('/api/v1/product/list', methods=['GET', 'POST'])
def product_list():
    try:
        db_session = g.db_session
        product_service = ProductService(db_session=db_session)

        context = {}
        if request.method == 'POST':
            context = request.json
        current_app.logger.info(context)

        log = AppApiLog(url='/api/v1/product/list', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        criteria = {
            'status': 'NORMAL',
            'category_id': context.get('category_id', ''),
            'keyword': context.get('keyword', '').strip()
        }
        item_list = product_service.api_find_product_by_criteria(criteria=copy(criteria))
        for item in item_list:
            item['description'] = ''

            color_image_map = {}
            product_color_image_list = product_service.find_all_product_color_image_by_product_id(product_id=item['id'])
            for color_image in product_color_image_list:
                color_image_map[color_image.color] = domain + color_image.image_url
            item['colorWithImage'] = color_image_map if len(color_image_map) > 0 else None

            product_image_payload = []
            product_image_list = product_service.find_all_product_image_by_product_id(product_id=item['id'])
            for product_image in product_image_list:
                product_image_payload.append(domain + product_image.image_url)
            item['images'] = product_image_payload if len(product_image_payload) > 0 else None

            for color_image in product_color_image_list:
                product_image_payload.append(domain + color_image.image_url)

        product_color_list = product_service.find_all_product_color()
        colors = {}
        for product_color in product_color_list:
            colors[product_color.title] = product_color.code

        payload = {
            'result': 1,
            'data': {
                'items': item_list,
                'colors': colors
            }
        }
        current_app.logger.info(payload)

        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)
    except Exception as e:
        payload = {'result': 0, 'message': '系統錯誤請稍後再試'}
        current_app.logger.info(traceback.format_exc())
        return jsonify(payload)


@v1_api_product_handler.route('/api/v1/product/detail/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    try:
        db_session = g.db_session
        product_service = ProductService(db_session=db_session)

        log = AppApiLog(url='/api/v1/product/detail/{}'.format(product_id), request_body=json.dumps({}, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        product = product_service.find_product_by_id(product_id=product_id)
        if not product or product.removed or product.status != ProductStatus.NORMAL:
            payload = {'result': 0, 'message': '商品不存在'}
            current_app.logger.info(payload)

            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        product_payload = {
            'id': product.id,
            'title': product.title,
            'description': '',
            'content': '<style>p{margin-top:0px; margin-bottom:0px}</style><div>' + product.content.replace('\r', '').replace('\n', '') + '</div>',
            'price': product.price,
        }

        color_image_map = {}
        product_color_image_list = product_service.find_all_product_color_image_by_product_id(product_id=product.id)
        for color_image in product_color_image_list:
            color_image_map[color_image.color] = domain + color_image.image_url
        product_payload['colorWithImage'] = color_image_map if len(color_image_map) > 0 else None

        product_image_payload = []
        product_image_list = product_service.find_all_product_image_by_product_id(product_id=product.id)
        for product_image in product_image_list:
            product_image_payload.append(domain + product_image.image_url)
        product_payload['images'] = product_image_payload

        for color_image in product_color_image_list:
            product_image_payload.append(domain + color_image.image_url)

        product_color_list = product_service.find_all_product_color()
        colors = {}
        for product_color in product_color_list:
            colors[product_color.title] = product_color.code

        specific_order_list = []
        specific_payload = {}
        specific_list = product_service.find_all_product_specific_by_product_id(product_id=product.id)
        for specific in specific_list:
            specific_order_list.append(specific.title)
            specific_payload[specific.title] = json.loads(specific.color_list)
        product_payload['specificOrder'] = specific_order_list
        product_payload['specific'] = specific_payload if len(specific_payload) > 0 else None

        payload = {
            'result': 1,
            'data': {
                'item': product_payload,
                'colors': colors if len(colors) > 0 else None
            }
        }
        current_app.logger.info(payload)

        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)
    except Exception as e:
        payload = {'result': 0, 'message': '系統錯誤請稍後再試'}
        current_app.logger.info(traceback.format_exc())
        return jsonify(payload)
