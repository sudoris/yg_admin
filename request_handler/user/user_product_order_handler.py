# -*- coding: utf-8 -*-
from app_config.config import (
    domain, member_line_channel_access_token
)
import os
import json
import traceback
import xlsxwriter
from copy import copy
from datetime import datetime
from flask import Blueprint, request, redirect, make_response, session, send_file, json, current_app, jsonify, g
from request_handler.user.user_request_helper import check_user_login, render_template
from linebot import LineBotApi
from linebot.models import TextSendMessage
from app_model.member_model import MemberMessage
from app_model.order_model import OrderStatus, Gender, Payment
from app_service.order_service import OrderService
from app_service.member_service import MemberService


row_per_page = 10
user_product_order_handler = Blueprint('user_product_order_handler', __name__)


@user_product_order_handler.route('/dashboard/user/product/order/list', methods=['GET', 'POST'])
@user_product_order_handler.route('/dashboard/user/product/order/list/<int:page>', methods=['GET', 'POST'])
@check_user_login
def order_list(user_id, page=1):
    db_session = g.db_session
    order_service = OrderService(db_session=db_session)

    criteria = {
        'no': request.values.get('no', '').strip(),
        'identify_no': request.values.get('identify_no', '').strip(),
        'card_no': request.values.get('card_no', '').strip(),
        'status': request.values.get('status', ''),
        'name': request.values.get('name', ''),
        'mobile': request.values.get('mobile', ''),
        'create_datetime_start': request.values.get('create_datetime_start', ''),
        'create_datetime_end': request.values.get('create_datetime_end', '')
    }
    total_count, item_list = order_service.find_order_primary_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)
    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    for item in item_list:
        _, order_detail_list = order_service.find_order_detail_by_primary_id(primary_id=item['id'])
        item['order_detail'] = order_detail_list

    template_path = 'user/pages/order/order_list.html'
    return render_template(template_path,
                           item_list=item_list,
                           OrderStatus=OrderStatus,
                           Gender=Gender,
                           Payment=Payment,
                           criteria=criteria,
                           page=page,
                           total_page=total_page,
                           row_per_page=row_per_page)


@user_product_order_handler.route('/dashboard/user/product/order/list/download', methods=['GET', 'POST'])
@check_user_login
def order_download(user_id):
    db_session = g.db_session
    order_service = OrderService(db_session=db_session)

    criteria = {
        'no': request.values.get('no', '').strip(),
        'identify_no': request.values.get('identify_no', '').strip(),
        'card_no': request.values.get('card_no', '').strip(),
        'status': request.values.get('status', ''),
        'name': request.values.get('name', ''),
        'mobile': request.values.get('mobile', ''),
        'create_datetime_start': request.values.get('create_datetime_start', ''),
        'create_datetime_end': request.values.get('create_datetime_end', '')
    }

    _, item_list = order_service.find_order_primary_by_criteria(criteria=copy(criteria), page=1, row_per_page=999999999)
    order_detail_count_list = []
    order_detail_list = []
    for item in item_list:
        total_count, order_detail = order_service.find_order_detail_by_primary_id(primary_id=item['id'])

        if total_count == 0:
            total_count = 1
        order_detail_count_list.append(total_count)

        if order_detail:
            order_detail_list.extend(order_detail)
        else:
            order_detail_list.append(None)

    assert len(item_list) == len(order_detail_count_list)
    assert len(order_detail_list) == sum(order_detail_count_list)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(os.getcwd(), 'private', 'order_{}.xlsx'.format(timestamp))

    workbook = xlsxwriter.Workbook(path)
    header_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'top',
        'align': 'center',
        'bold': True,
        'font_size': 20
    })
    text_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'top',
        'font_size': 16
    })
    clear_format = workbook.add_format({'font_size': 16})
    money_format = workbook.add_format({'num_format': '#,##', 'font_size': 16})
    number_format = workbook.add_format({
        'num_format': '#,##',
        'font_size': 16
    })

    worksheet = workbook.add_worksheet()
    worksheet.set_column(0, 0, 10)  # 項次
    worksheet.set_column(1, 1, 25)  # 訂單編號
    worksheet.set_column(2, 2, 25)  # 會員卡號
    worksheet.set_column(3, 3, 25)  # 會員姓名
    worksheet.set_column(4, 4, 25)  # 會員編號
    worksheet.set_column(5, 5, 15)  # 總金額
    worksheet.set_column(6, 6, 20)  # 訂單狀態
    worksheet.set_column(7, 7, 10)  # 姓名
    worksheet.set_column(8, 8, 25)  # 性別
    worksheet.set_column(9, 9, 25)  # 手機
    worksheet.set_column(10, 10, 80)  # 地址
    worksheet.set_column(11, 11, 50)  # 欲扣值順序
    worksheet.set_column(12, 12, 30)  # 訂單建立時間
    worksheet.set_column(13, 13, 80)  # 商品名稱
    worksheet.set_column(14, 14, 15)  # 商品價格
    worksheet.set_column(15, 15, 15)  # 商品規格
    worksheet.set_column(16, 16, 15)  # 商品顏色
    worksheet.set_column(17, 17, 10)  # 數量

    worksheet.write_string(0, 0, '項次', text_format)
    worksheet.write_string(0, 1, '訂單編號', text_format)
    worksheet.write_string(0, 2, '會員卡號', text_format)
    worksheet.write_string(0, 3, '會員姓名', text_format)
    worksheet.write_string(0, 4, '會員編號', text_format)
    worksheet.write_string(0, 5, '總金額', text_format)
    worksheet.write_string(0, 6, '訂單狀態', text_format)
    worksheet.write_string(0, 7, '姓名', text_format)
    worksheet.write_string(0, 8, '性別', text_format)
    worksheet.write_string(0, 9, '手機', text_format)
    worksheet.write_string(0, 10, '地址', text_format)
    worksheet.write_string(0, 11, '欲扣值順序', text_format)
    worksheet.write_string(0, 12, '訂單建立時間', text_format)
    worksheet.write_string(0, 13, '商品名稱', text_format)
    worksheet.write_string(0, 14, '商品價格', text_format)
    worksheet.write_string(0, 15, '商品規格', text_format)
    worksheet.write_string(0, 16, '商品顏色', text_format)
    worksheet.write_string(0, 17, '數量', text_format)

    row = 1
    for item, order_detail_count in zip(item_list, order_detail_count_list):
        payment = f'{Payment[item["payment_1"]].value} > {Payment[item["payment_2"]].value} > {Payment[item["payment_3"]].value}'
        if item['memo']:
            payment += f' \n 備註 \n {item["memo"]}'
        if order_detail_count == 1:
            worksheet.write_string(row, 0, str(item['id']), text_format)
            worksheet.write_string(row, 1, item['no'], text_format)
            worksheet.write_string(row, 2, item['card_no'], text_format)
            worksheet.write_string(row, 3, item['mem_member_name'], text_format)
            worksheet.write_string(row, 4, item['mem_member_no'], text_format)
            worksheet.write_number(row, 5, item['total_price'], money_format)
            worksheet.write_string(row, 6, OrderStatus[item['status']].value, text_format)
            worksheet.write_string(row, 7, item['name'], text_format)
            worksheet.write_string(row, 8, Gender[item['gender']].value, text_format)
            worksheet.write_string(row, 9, item['mobile'], text_format)
            worksheet.write_string(row, 10, item['address'], text_format)
            worksheet.write_string(row, 11, payment, text_format)
            worksheet.write_string(row, 12, item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S'), text_format)
            row += 1
        else:
            start = row
            end = start + order_detail_count - 1
            worksheet.merge_range(start, 0, end, 0, str(item['id']),
                                  text_format)
            worksheet.merge_range(start, 1, end, 1, item['no'], text_format)
            worksheet.merge_range(start, 2, end, 2, item['card_no'],
                                  text_format)
            worksheet.merge_range(start, 3, end, 3, item['mem_member_name'],
                                  text_format)
            worksheet.merge_range(start, 4, end, 4, item['mem_member_no'],
                                  text_format)
            worksheet.merge_range(start, 5, end, 5, item['total_price'],
                                  money_format)
            worksheet.merge_range(start, 6, end, 6,
                                  OrderStatus[item['status']].value,
                                  text_format)
            worksheet.merge_range(start, 7, end, 7, item['name'], text_format)
            worksheet.merge_range(start, 8, end, 8,
                                  Gender[item['gender']].value, text_format)
            worksheet.merge_range(start, 9, end, 9, item['mobile'],
                                  text_format)
            worksheet.merge_range(start, 10, end, 10, item['address'],
                                  text_format)
            worksheet.merge_range(start, 11, end, 11, payment, text_format)
            worksheet.merge_range(
                start, 12, end, 12,
                item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                text_format)
            row += order_detail_count

    row = 1
    for item in order_detail_list:
        if not item:
            worksheet.write_blank(row, 13, '', clear_format)
            worksheet.write_blank(row, 14, '', clear_format)
            worksheet.write_blank(row, 15, '', clear_format)
            worksheet.write_blank(row, 16, '', clear_format)
            worksheet.write_blank(row, 17, '', clear_format)
            row += 1
            continue

        if item.get('title'):
            worksheet.write_string(row, 13, item['title'], text_format)
        else:
            worksheet.write_blank(row, 13, '', clear_format)

        if item.get('price'):
            worksheet.write_number(row, 14, item['price'], money_format)
        else:
            worksheet.write_blank(row, 14, '', clear_format)

        if item.get('specific'):
            worksheet.write_string(row, 15, item['specific'], text_format)
        else:
            worksheet.write_blank(row, 15, '', clear_format)

        if item.get('color'):
            worksheet.write_string(row, 16, item['color'], text_format)
        else:
            worksheet.write_blank(row, 16, '', clear_format)

        if item.get('quantity'):
            worksheet.write_number(row, 17, int(item['quantity']),
                                   number_format)
        else:
            worksheet.write_blank(row, 17, '', clear_format)

        row += 1

    workbook.close()
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    response = make_response(
        send_file(
            path,
            mimetype=
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name='訂單_{}.xlsx'.format(timestamp),
            as_attachment=True))
    response.headers['max-age'] = '0'
    response.headers['Cache-Control'] = 'no-store'
    return response


@user_product_order_handler.route('/dashboard/user/product/order/list/download/v2', methods=['GET', 'POST'])
@check_user_login
def order_download_v2():
    db_session = g.db_session
    order_service = OrderService(db_session=db_session)

    criteria = {
        'status':
            request.values.get('status', ''),
        'name':
            request.values.get('name', ''),
        'mobile':
            request.values.get('mobile', ''),
        'create_datetime_start':
            request.values.get('create_datetime_start', ''),
        'create_datetime_end':
            request.values.get('create_datetime_end', '')
    }

    item_list = order_service.find_order_by_criteria(criteria=copy(criteria),
                                                     page=1,
                                                     row_per_page=999999999)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(os.getcwd(), 'private',
                        'product_1_{}.xlsx'.format(timestamp))

    workbook = xlsxwriter.Workbook(path)
    header_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'top',
        'align': 'center',
        'bold': True,
        'font_size': 20
    })
    text_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'top',
        'font_size': 16
    })
    clear_format = workbook.add_format({'font_size': 16})
    money_format = workbook.add_format({'num_format': '#,##', 'font_size': 16})
    number_format = workbook.add_format({
        'num_format': '#,##',
        'font_size': 16
    })

    worksheet = workbook.add_worksheet()
    worksheet.set_column(0, 0, 10)  # 項次
    worksheet.set_column(1, 1, 25)  # 訂單編號
    worksheet.set_column(2, 2, 25)  # 會員卡號
    worksheet.set_column(3, 3, 15)  # 總金額
    worksheet.set_column(4, 4, 20)  # 訂單狀態
    worksheet.set_column(5, 5, 25)  # 手機
    worksheet.set_column(6, 6, 30)  # 訂單建立時間
    worksheet.set_column(7, 7, 80)  # 商品名稱
    worksheet.set_column(8, 8, 15)  # 商品價格
    worksheet.set_column(9, 9, 15)  # 商品顏色
    worksheet.set_column(10, 10, 10)  # 數量

    worksheet.write_string(0, 0, '項次', text_format)
    worksheet.write_string(0, 1, '訂單編號', text_format)
    worksheet.write_string(0, 2, '會員卡號', text_format)
    worksheet.write_string(0, 3, '總金額', text_format)
    worksheet.write_string(0, 4, '訂單狀態', text_format)
    worksheet.write_string(0, 5, '手機', text_format)
    worksheet.write_string(0, 6, '訂單建立時間', text_format)
    worksheet.write_string(0, 7, '商品名稱', text_format)
    worksheet.write_string(0, 8, '商品價格', text_format)
    worksheet.write_string(0, 9, '商品顏色', text_format)
    worksheet.write_string(0, 10, '數量', text_format)

    pos_list = []
    id_list = [item['id'] for item in item_list]
    specific_id_list = list(dict.fromkeys(id_list))
    specific_id_list_cp = specific_id_list.copy()
    start = 1
    for id in specific_id_list:
        num = id_list.count(id)
        end = start + num - 1
        pos_list.append((start, end))
        start += num

    first_time_shown_list = []
    for id in id_list:
        if id in specific_id_list_cp:
            first_time_shown_list.append(True)
            specific_id_list_cp.remove(id)
        else:
            first_time_shown_list.append(False)

    row = 1
    for item, first_time_shown in zip(item_list, first_time_shown_list):
        id = item['id']
        if first_time_shown:
            index = specific_id_list.index(id)
            start = pos_list[index][0]
            end = pos_list[index][1]
            if start == end:
                worksheet.write_string(row, 0, str(item['id']), text_format)
                worksheet.write_string(row, 1, item['no'], text_format)
                worksheet.write_string(row, 2, item['card_no'], text_format)
                worksheet.write_number(row, 3, item['total_price'],
                                       money_format)
                worksheet.write_string(row, 4,
                                       OrderStatus[item['status']].value,
                                       text_format)
                worksheet.write_string(row, 5, item['mobile'], text_format)
                worksheet.write_string(
                    row, 6,
                    item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                    text_format)
            else:
                worksheet.merge_range(start, 0, end, 0, str(item['id']),
                                      text_format)
                worksheet.merge_range(start, 1, end, 1, item['no'],
                                      text_format)
                worksheet.merge_range(start, 2, end, 2, item['card_no'],
                                      text_format)
                worksheet.merge_range(start, 3, end, 3, item['total_price'],
                                      money_format)
                worksheet.merge_range(start, 4, end, 4,
                                      OrderStatus[item['status']].value,
                                      text_format)
                worksheet.merge_range(start, 5, end, 5, item['mobile'],
                                      text_format)
                worksheet.merge_range(
                    start, 6, end, 6,
                    item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                    text_format)

        if item.get('title'):
            worksheet.write_string(row, 7, item['title'], text_format)
        else:
            worksheet.write_blank(row, 7, '', clear_format)

        if item.get('price'):
            worksheet.write_number(row, 8, item['price'], money_format)
        else:
            worksheet.write_blank(row, 8, '', clear_format)

        if item.get('color'):
            worksheet.write_string(row, 9, item['color'], text_format)
        else:
            worksheet.write_blank(row, 9, '', clear_format)

        if item.get('quantity'):
            worksheet.write_number(row, 10, int(item['quantity']),
                                   number_format)
        else:
            worksheet.write_blank(row, 10, '', clear_format)

        row += 1

    workbook.close()
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    response = make_response(
        send_file(
            path,
            mimetype=
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name='訂單_{}.xlsx'.format(timestamp),
            as_attachment=True))
    response.headers['max-age'] = '0'
    response.headers['Cache-Control'] = 'no-store'
    return response


@user_product_order_handler.route('/dashboard/user/product/order/ajax-load-remark', methods=['GET', 'POST'])
@check_user_login
def ajax_load_order_remark_handler(user_id):
    db_session = g.db_session
    order_service = OrderService(db_session=db_session)

    context = request.json
    current_app.logger.info(context)

    primary = order_service.find_order_primary_by_id(primary_id=context['primary_id'])
    if not primary:
        return jsonify({'result': 0, 'message': '找不到訂單'})

    payload = {
        'result': 1,
        'remark': primary.remark
    }
    return jsonify(payload)


@user_product_order_handler.route('/dashboard/user/product/order/ajax-save-remark', methods=['GET', 'POST'])
@check_user_login
def ajax_save_order_remark_handler(user_id):
    db_session = g.db_session
    order_service = OrderService(db_session=db_session)

    context = request.json
    current_app.logger.info(context)

    primary = order_service.find_order_primary_by_id(primary_id=context['primary_id'])
    if not primary:
        return jsonify({'result': 0, 'message': '找不到訂單'})

    remark = context.get('remark', '')
    primary.remark = remark
    db_session.commit()

    payload = {'result': 1}
    return jsonify(payload)


@user_product_order_handler.route('/dashboard/user/product/order/ajax-change-status', methods=['GET', 'POST'])
@check_user_login
def ajax_change_order_status_handler(user_id):
    """ Ajax變更訂單狀態 """
    db_session = g.db_session
    order_service = OrderService(db_session=db_session)

    context = request.json
    current_app.logger.info(context)

    primary = order_service.find_order_primary_by_id(primary_id=context['primary_id'])
    if not primary:
        return jsonify({'result': 0, 'message': '找不到訂單'})

    status = context.get('status', '')
    if not status:
        return jsonify({'result': 0, 'message': '狀態錯誤'})

    primary.status = status
    db_session.commit()

    payload = {'result': 1}
    return jsonify(payload)


@user_product_order_handler.route('/dashboard/user/product/order/ajax-save-message', methods=['GET', 'POST'])
@check_user_login
def ajax_send_message_handler(user_id):
    db_session = g.db_session
    order_service = OrderService(db_session=db_session)
    member_service = MemberService(db_session=db_session)

    context = request.json
    current_app.logger.info(context)

    message = context.get('message', '').strip()
    if not message:
        return jsonify({'result': 0, 'message': '訊息不得為空'})

    primary = order_service.find_order_primary_by_id(primary_id=context['primary_id'])
    if not primary:
        return jsonify({'result': 0, 'message': '找不到訂單'})

    content = [{'type': 'TEXT', 'content': message}]

    member_message = MemberMessage()
    member_message.create(card_no=primary.card_no, title='訂單通知', description='', content=json.dumps(content, ensure_ascii=False), order_id=primary.id)
    db_session.add(member_message)
    db_session.commit()

    try:
        member_line_info = member_service.find_member_line_info_by_id(member_line_info_id=primary.line_info_id)
        line_bot_api = LineBotApi(member_line_channel_access_token)
        messages = [TextSendMessage(text=message)]
        line_bot_api.push_message(member_line_info.line_user_id, messages)
    except Exception:
        current_app.logger.error(traceback.format_exc())

    payload = {'result': 1}
    return jsonify(payload)
