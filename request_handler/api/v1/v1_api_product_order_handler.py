# -*- coding: utf-8 -*-
from app_config.config import (
    domain
)
import json
import traceback
from datetime import datetime
from flask import Blueprint, request, current_app, jsonify, g
from request_handler.core.core_request_helper import get_real_ip
from request_handler.api.api_request_helper import check_line_info_login
from app_model.log_model import AppApiLog
from app_model.product_model import ProductStatus
from app_model.order_model import OrderPrimary, OrderDetail, ShopCartItem
from app_service.order_service import OrderService
from app_service.product_service import ProductService


v1_api_product_order_handler = Blueprint('v1_api_product_order_handler', __name__)


@v1_api_product_order_handler.route('/api/v1/product/order/create', methods=['POST'])
@check_line_info_login
def order_create_handler(line_info_id, member_id, card_no):
    db_session = None
    log = None
    try:
        db_session = g.db_session
        order_service = OrderService(db_session=db_session)
        product_service = ProductService(db_session=db_session)

        context = request.json
        current_app.logger.info(context)

        log = AppApiLog(url='/api/v1/product/order/create', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        name = context.get('name', '').strip()
        gender = context.get('gender', '').strip()
        mobile = context.get('mobile', '').strip()
        address = context.get('address', '').strip()

        shop_card_item_list = order_service.find_all_shop_card_item_by_line_info_id(line_info_id=line_info_id)
        if len(shop_card_item_list) == 0:
            payload = {'result': 0, 'message': '購物車沒有商品'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        if not name:
            payload = {'result': 0, 'message': '請輸入姓名'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        if not mobile:
            payload = {'result': 0, 'message': '請輸入手機號碼'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        if not gender:
            payload = {'result': 0, 'message': '請選擇性別'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        if not address:
            payload = {'result': 0, 'message': '請輸入地址'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        payment_1 = context.get('payment1', '')
        payment_2 = context.get('payment2', '')
        payment_3 = context.get('payment3', '')

        if not payment_1 or not payment_2 or not payment_3:
            payload = {'result': 0, 'message': '請選擇付款順序'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        memo = context.get('memo', '')
        order_primary = OrderPrimary(line_info_id=line_info_id, member_id=member_id, card_no=card_no, name=name, gender=gender, mobile=mobile, address=address, payment_1=payment_1, payment_2=payment_2, payment_3=payment_3, memo=memo)
        db_session.add(order_primary)
        db_session.flush()

        order_count = order_service.count_order_primary_of_this_year()
        no = ''.join([datetime.now().strftime('%Y'), datetime.now().strftime('%m'), str(order_count).zfill(6)])
        order_primary.no = no

        total_price = 0

        for item in shop_card_item_list:
            product = product_service.find_product_by_id(item.product_id)
            if product and product.status == ProductStatus.NORMAL:
                total_price += product.price * item.quantity
                order_detail = OrderDetail(primary_id=order_primary.id, product_id=product.id, price=product.price, specific=item.specific, color=item.color, quantity=item.quantity)
                db_session.add(order_detail)
            item.quantity = 0

        order_primary.total_price = total_price
        db_session.commit()

        payload = {'result': 1}
        log.response_body = json.dumps(payload, ensure_ascii=False)
        db_session.commit()
        return jsonify(payload)

    except Exception as e:
        current_app.logger.info(traceback.format_exc())
        if db_session and log:
            log.response_body = traceback.format_exc()
            db_session.commit()

        payload = {'result': 0, 'message': '系統錯誤'}
        return jsonify(payload)


@v1_api_product_order_handler.route('/api/v1/product/shop-cart/list', methods=['GET', 'POST'])
@check_line_info_login
def shop_card_item_list_handler(line_info_id, member_id, card_no):
    db_session = None
    log = None
    try:
        db_session = g.db_session

        log = AppApiLog(url='/api/v1/product/shop-cart/list', request_body='', ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        total_price, total_item_count, items_payload = build_shop_card_item_payload(line_info_id=line_info_id, db_session=db_session)
        payload = {
            'result': 1,
            'data': {
                'items': items_payload,
                'totalPrice': total_price,
                'totalItemNumber': total_item_count
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

        payload = {'result': 0, 'message': '系統錯誤'}
        return jsonify(payload)


@v1_api_product_order_handler.route('/api/v1/product/shop-cart/plus', methods=['POST'])
@check_line_info_login
def shop_card_item_add_handler(line_info_id, member_id, card_no):
    db_session = None
    log = None
    try:
        db_session = g.db_session
        order_service = OrderService(db_session=db_session)
        product_service = ProductService(db_session=db_session)

        context = request.json
        current_app.logger.info(context)

        log = AppApiLog(url='/api/v1/product/shop-cart/plus', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        product_id = context.get('id', '')
        specific = context.get('specific', '').strip()
        color = context.get('color', '').strip()
        quantity = int(context.get('quantity', 1))

        if not product_id:
            payload = {'result': 0, 'message': '請選擇商品'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        product = product_service.find_product_by_id(product_id)
        if not product or product.status != ProductStatus.NORMAL:
            payload = {'result': 0, 'message': '商品已下架'}
            log.response_body = json.dumps(payload, ensure_ascii=False)
            db_session.commit()
            return jsonify(payload)

        product_specific_list = product_service.find_all_product_specific_by_product_id(product_id=product_id)
        if product_specific_list and len(product_specific_list) > 0:
            if not specific:
                payload = {'result': 0, 'message': '請選擇規格'}
                log.response_body = json.dumps(payload, ensure_ascii=False)
                db_session.commit()
                return jsonify(payload)

            product_specific = product_service.find_product_specific_by_product_id_and_title(product_id=product_id, title=specific)
            if product_specific and product_specific.color_list:
                color_list = json.loads(product_specific.color_list)
                if color_list and len(color_list) and not color:
                    payload = {'result': 0, 'message': '請選擇顏色'}
                    log.response_body = json.dumps(payload, ensure_ascii=False)
                    db_session.commit()
                    return jsonify(payload)

        shop_card_item = order_service.find_shop_card_item_by_line_info_id_and_product_id_and_specific_and_color(line_info_id=line_info_id, product_id=product_id, specific=specific, color=color)
        if not shop_card_item:
            shop_card_item = ShopCartItem(line_info_id=line_info_id, product_id=product_id, specific=specific, color=color, quantity=quantity)
            db_session.add(shop_card_item)
        else:
            shop_card_item.quantity += quantity
        db_session.commit()

        total_price, total_item_count, items_payload = build_shop_card_item_payload(line_info_id=line_info_id, db_session=db_session)
        payload = {
            'result': 1,
            'data': {
                'items': items_payload,
                'totalPrice': total_price,
                'totalItemNumber': total_item_count
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

        payload = {'result': 0, 'message': '系統錯誤'}
        return jsonify(payload)


@v1_api_product_order_handler.route('/api/v1/product/shop-cart/minus', methods=['POST'])
@check_line_info_login
def shop_card_item_minus_handler(line_info_id, member_id, card_no):
    db_session = None
    log = None
    try:
        db_session = g.db_session
        order_service = OrderService(db_session=db_session)
        product_service = ProductService(db_session=db_session)

        context = request.json
        current_app.logger.info(context)

        log = AppApiLog(url='/api/v1/product/shop-cart/minus', request_body=json.dumps(context, ensure_ascii=False), ip=get_real_ip())
        db_session.add(log)
        db_session.commit()

        product_id = context.get('id', '')
        specific = context.get('specific', '').strip()
        color = context.get('color', '').strip()
        quantity = int(context.get('quantity', 1))

        shop_card_item = order_service.find_shop_card_item_by_line_info_id_and_product_id_and_specific_and_color(line_info_id=line_info_id, product_id=product_id, specific=specific, color=color)
        if shop_card_item:
            shop_card_item.quantity -= quantity
            if shop_card_item.quantity <= 0:
                shop_card_item.quantity = 0
            db_session.commit()

        total_price, total_item_count, items_payload = build_shop_card_item_payload(line_info_id=line_info_id, db_session=db_session)
        payload = {
            'result': 1,
            'data': {
                'items': items_payload,
                'totalPrice': total_price,
                'totalItemNumber': total_item_count
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
        payload = {'result': 0, 'message': '系統錯誤'}
        return jsonify(payload)


def build_shop_card_item_payload(line_info_id, db_session):
    order_service = OrderService(db_session=db_session)
    product_service = ProductService(db_session=db_session)

    total_price = 0
    total_item_count = 0
    items_payload = []
    shop_card_item_list = order_service.find_all_shop_card_item_by_line_info_id(line_info_id=line_info_id)
    for item in shop_card_item_list:
        product = product_service.find_product_by_id(item.product_id)
        if product and product.status == ProductStatus.NORMAL:
            image = '#'
            if item.color:
                color_image = product_service.find_product_color_image_by_product_id_and_color(product_id=item.product_id, color=item.color)
                if color_image:
                    image = domain + color_image.image_url

            if image == '#':
                product_image_list = product_service.find_all_product_image_by_product_id(product_id=item.product_id)
                if product_image_list and len(product_image_list) > 0:
                    product_image = product_image_list[0]
                    image = domain + product_image.image_url

            items_payload.append({
                'id': product.id,
                'title': product.title,
                'specific': item.specific,
                'color': item.color,
                'quantity': item.quantity,
                'price': product.price,
                'image': image
            })
            total_item_count += 1
            total_price += product.price * item.quantity

    return total_price, total_item_count, items_payload

