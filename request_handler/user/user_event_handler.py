# -*- coding: utf-8 -*-
from app_config.config import (
    domain, member_line_channel_access_token
)
import os
import traceback
import xlsxwriter
from copy import copy
from datetime import datetime
from flask import Blueprint, request, redirect, make_response, session, json, current_app, jsonify, send_file, g
from request_handler.user.user_request_helper import check_user_login, render_template
from app_service.event_service import EventService
from app_service.member_service import MemberService
from app_model.event_model import (
    EventPrimary,
    EventDetail,
    EventAndInterestRelation,
    RegisterStatus,
    RegisterPrimary,
    RegisterFamily,
    RegisterGuest,
    Payment,
)
from linebot import LineBotApi
from linebot.models import TextSendMessage
from app_model.member_model import MemberMessage
from app_model.event_model import PaymentStatus, EventStatus
from app_utility.athena_utility import query_data_by_card_no
from app_utility.file_utility import save_file
from app_utility.string_utility import StringUtility

row_per_page = 10
user_event_handler = Blueprint('user_event_handler', __name__)


@user_event_handler.route('/dashboard/user/event/list', methods=['GET', 'POST'])
@user_event_handler.route('/dashboard/user/event/list/<int:page>', methods=['GET', 'POST'])
@check_user_login
def event_list(user_id, page=1):
    db_session = g.db_session
    event_service = EventService(db_session=db_session)

    criteria = {
        'title': request.values.get('title', '').strip(),
        'status': request.values.get('status', '')
    }
    total_count, item_list = event_service.find_event_primary_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)

    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    template_path = 'user/pages/event/event_list.html'
    return render_template(
        template_path,
        item_list=item_list,
        total_page=total_page,
        page=page,
        criteria=criteria,
        r=StringUtility.generate_random_number_and_lowercase_letters(6))


@user_event_handler.route('/dashboard/user/event/create', methods=['GET', 'POST'])
@check_user_login
def event_create(user_id):
    """ 新增活動 """
    db_session = g.db_session
    event_service = EventService(db_session=db_session)

    event_primary = EventPrimary()
    if request.method == 'GET':
        interest_list = event_service.find_all_interest()
        template_path = 'user/pages/event/event_create.html'
        return render_template(template_path,
                               event_primary=event_primary,
                               interest_list=interest_list,
                               selected_interest_list=[],
                               detail_list=json.dumps([], ensure_ascii=False),
                               today=datetime.now().strftime('%Y-%m-%d'))
    """ POST """
    title = request.values.get('title', '').strip()
    description = request.values.get('description', '').strip()
    flag_top = request.values.get('flag_top', 0).strip()
    status = request.values.get('status', '').strip()
    start_date = request.values.get('start_date', '').strip()
    if not start_date:
        start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = request.values.get('end_date', '').strip()
    content = request.values.get('content', '').strip()
    content_fee = request.values.get('content_fee', '').strip()
    content_refund = request.values.get('content_refund', '').strip()
    detail_list = request.values.get('detail_list', '').strip()

    if 'cover_image' in request.files and request.files['cover_image']:
        upload_file = request.files['cover_image']
        event_primary.cover_image = save_file(upload_file=upload_file,
                                              prefix='event')
        db_session.commit()

    event_primary.create(title=title, description=description, content=content, content_fee=content_fee, content_refund=content_refund, status=status,
                         flag_top=flag_top, start_date=start_date, end_date=end_date, create_user_id=user_id)
    db_session.add(event_primary)
    db_session.flush()

    for detail in json.loads(detail_list):
        if detail['removed'] == 0:
            event_detail = EventDetail(primary_id=event_primary.id,
                                       location=detail['location'],
                                       time=detail['time'],
                                       limit=detail['limit'],
                                       end_date=detail['end_date'],
                                       create_user_id=user_id)
            db_session.add(event_detail)

    db_session.commit()

    interest_id_list = request.form.getlist('interest_id_list')
    mapping_event_and_interest(event=event_primary,
                               interest_id_list=interest_id_list,
                               db_session=db_session)

    return redirect('/dashboard/user/event/update/{}?result=1&message={}'.format(event_primary.id, '新增成功'))


@user_event_handler.route('/dashboard/user/event/update/<int:primary_id>', methods=['GET', 'POST'])
@check_user_login
def event_update(user_id, primary_id):
    db_session = g.db_session
    event_service = EventService(db_session=db_session)

    event_primary = event_service.find_event_primary_by_id(primary_id=primary_id)
    if not event_primary or event_primary.removed:
        return redirect('/dashboard/user/event/list')

    if request.method == 'GET':
        event_detail_payload = []
        event_detail_list = event_service.find_all_event_detail_by_primary_id(primary_id=primary_id)
        for event_detail in event_detail_list:
            event_detail_payload.append({
                'id': event_detail.id,
                'location': event_detail.location,
                'time': event_detail.time,
                'limit': event_detail.limit,
                'end_date': event_detail.end_date.strftime('%Y-%m-%d') if event_detail.end_date else '',
                'removed': 0
            })

        interest_list = event_service.find_all_interest()
        selected_interest_list = event_service.find_interest_list_by_event_id(event_id=primary_id)
        template_path = 'user/pages/event/event_update.html'
        return render_template(template_path, event_primary=event_primary, interest_list=interest_list, selected_interest_list=selected_interest_list,
                               detail_list=json.dumps(event_detail_payload, ensure_ascii=False), today=datetime.now().strftime('%Y-%m-%d'))

    """ POST """
    title = request.values.get('title', '').strip()
    description = request.values.get('description', '').strip()
    flag_top = request.values.get('flag_top', 0).strip()
    status = request.values.get('status', '').strip()
    start_date = request.values.get('start_date', '').strip()
    if not start_date:
        start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = request.values.get('end_date', '').strip()
    content = request.values.get('content', '').strip()
    content_fee = request.values.get('content_fee', '').strip()
    content_refund = request.values.get('content_refund', '').strip()
    detail_list = request.values.get('detail_list', '').strip()

    event_primary.update(title=title, description=description, content=content, content_fee=content_fee, content_refund=content_refund,
                         status=status, flag_top=flag_top, start_date=start_date, end_date=end_date, update_user_id=user_id)

    if 'cover_image' in request.files and request.files['cover_image']:
        upload_file = request.files['cover_image']
        event_primary.cover_image = save_file(upload_file=upload_file, prefix='event')
        db_session.commit()

    for detail in json.loads(detail_list):
        if detail['id'] and detail['removed'] == 0:
            detail_item = event_service.find_event_detail_by_id(detail_id=detail['id'])
            detail_item.update(location=detail['location'], time=detail['time'], limit=detail['limit'], end_date=detail['end_date'], update_user_id=user_id)
        elif detail['id'] and detail['removed'] == 1:
            detail_item = event_service.find_event_detail_by_id(detail_id=detail['id'])
            detail_item.delete(update_user_id=user_id)
        elif not detail['id'] and detail['removed'] == 0:
            event_detail = EventDetail(primary_id=event_primary.id, location=detail['location'], time=detail['time'], limit=detail['limit'], end_date=detail['end_date'], create_user_id=user_id)
            db_session.add(event_detail)

    db_session.commit()

    interest_id_list = request.form.getlist('interest_id_list')
    mapping_event_and_interest(event=event_primary, interest_id_list=interest_id_list, db_session=db_session)

    return redirect('/dashboard/user/event/update/{}?result=1&message={}'.format(event_primary.id, '更新成功'))


@user_event_handler.route('/dashboard/user/event/copy/<int:primary_id>', methods=['GET', 'POST'])
@check_user_login
def event_copy(user_id, primary_id):
    db_session = g.db_session
    event_service = EventService(db_session=db_session)

    event_primary = event_service.find_event_primary_by_id(primary_id=primary_id)
    if not event_primary or event_primary.removed:
        return redirect('/dashboard/user/event/list')

    new_event_primary = EventPrimary()
    new_event_primary.create(title=event_primary.title + "(複製)", description=event_primary.description, content=event_primary.content, content_fee=event_primary.content_fee, content_refund=event_primary.content_refund, status=EventStatus.SUSPENDED,
                             flag_top=event_primary.flag_top, start_date=event_primary.start_date, end_date=event_primary.end_date, create_user_id=user_id)
    new_event_primary.cover_image = event_primary.cover_image
    db_session.add(new_event_primary)
    db_session.commit()
    return redirect('/dashboard/user/event/list')


@user_event_handler.route('/dashboard/user/event/ajax-upload-image', methods=['GET', 'POST'])
@check_user_login
def event_ajax_upload_image(user_id):
    payload = {'success': 1}
    if 'image' in request.files and request.files['image']:
        upload_file = request.files['image']
        payload['file'] = {
            'url': save_file(upload_file=upload_file, prefix='event')
        }

    return jsonify(payload)


def mapping_event_and_interest(event: EventPrimary, interest_id_list,
                               db_session):
    for interest_id in interest_id_list:
        relation = db_session.query(EventAndInterestRelation).filter_by(
            event_id=event.id, interest_id=interest_id).first()

        if relation and relation.removed == 0:
            """ Relation 存在 , 不處理 """
            pass
        elif relation and relation.removed == 1:
            """ Relation 存在 , 但被移除 加回來 """
            relation.update(removed=0)
            db_session.commit()
        elif not relation:
            """ Relation 不存在 """
            relation = EventAndInterestRelation()
            relation.create(event_id=event.id, interest_id=interest_id)
            db_session.add(relation)
            db_session.commit()
    """ 移除 沒有被選擇的 Relation """
    removed_relation_list = db_session.query(EventAndInterestRelation). \
        filter(EventAndInterestRelation.interest_id.notin_(interest_id_list),
               EventAndInterestRelation.event_id == event.id,
               EventAndInterestRelation.removed == 0).all()

    for relation in removed_relation_list:
        relation.update(removed=1)
        db_session.commit()


@user_event_handler.route('/dashboard/user/event/<int:primary_id>/detail/list', methods=['GET', 'POST'])
@user_event_handler.route('/dashboard/user/event/<int:primary_id>/detail/list/<int:page>', methods=['GET', 'POST'])
@check_user_login
def event_detail_list_handler(user_id, primary_id, page=1):
    db_session = g.db_session
    event_service = EventService(db_session=db_session)

    primary = event_service.find_event_primary_by_id(primary_id=primary_id)
    if not primary:
        return redirect('/dashboard/user/event/list')

    criteria = {}
    total_count, item_list = event_service.find_event_detail_by_primary_id_and_page(primary_id=primary_id, criteria=copy(criteria), page=page, row_per_page=row_per_page)
    for item in item_list:
        count_register = 0
        register_primary_list = db_session.query(RegisterPrimary).filter_by(event_detail_id=item['id'], removed=0).all()
        count_register += len(register_primary_list)

        primary_id_list = []
        for register_primary in register_primary_list:
            primary_id_list.append(register_primary.id)

        register_family_list = db_session.query(RegisterFamily).filter(RegisterFamily.primary_id.in_(primary_id_list), RegisterFamily.removed == 0).all()
        count_register += len(register_family_list)

        register_guest_list = db_session.query(RegisterGuest).filter(RegisterGuest.primary_id.in_(primary_id_list), RegisterGuest.removed == 0).all()
        count_register += len(register_guest_list)

        item['count_register'] = count_register

    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    template_path = 'user/pages/event/event_detail_list.html'
    return render_template(template_path, primary=primary, item_list=item_list, total_page=total_page, page=page, criteria=criteria,
                           r=StringUtility.generate_random_number_and_lowercase_letters(6))


@user_event_handler.route('/dashboard/user/event/<int:primary_id>/detail/<int:event_detail_id>/register/list', methods=['GET', 'POST'])
@user_event_handler.route('/dashboard/user/event/<int:primary_id>/detail/<int:event_detail_id>/register/list/<int:page>', methods=['GET', 'POST'])
@check_user_login
def register_list(user_id, primary_id, event_detail_id, page=1):
    db_session = g.db_session
    event_service = EventService(db_session=db_session)

    event_primary = event_service.find_event_primary_by_id(primary_id=primary_id)
    event_detail = event_service.find_event_detail_by_id(detail_id=event_detail_id)

    criteria = {
        'card_no': request.values.get('card_no', '').strip(),
        'status': request.values.get('status', ''),
        'payment_status': request.values.get('payment_status', '')
    }
    total_count, item_list = event_service.find_register_primary_by_event_detail_id_and_page(event_detail_id=event_detail_id, criteria=copy(criteria), page=page, row_per_page=999999999999)

    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    for item in item_list:
        register_family_total_count, register_family_list = event_service.find_register_family_by_primary_id(primary_id=item['id'])
        register_guest_total_count, register_guest_list = event_service.find_register_guest_by_primary_id(primary_id=item['id'])
        register_family_list.extend(register_guest_list)
        item['register_invite'] = register_family_list
        item['sum'] = 1 + register_family_total_count + register_guest_total_count

    template_path = 'user/pages/event/event_register_list.html'
    return render_template(template_path, primary_id=primary_id, event_primary=event_primary,
                           event_detail_id=event_detail_id, event_detail=event_detail,
                           item_list=item_list, RegisterStatus=RegisterStatus, Payment=Payment, criteria=criteria, page=page, total_page=total_page, row_per_page=row_per_page,
                           r=StringUtility.generate_random_number_and_lowercase_letters(6))


@user_event_handler.route('/dashboard/user/event/<int:primary_id>/detail/<int:event_detail_id>/register/list/download', methods=['GET', 'POST'])
@check_user_login
def register_download(user_id, primary_id, event_detail_id):
    db_session = g.db_session
    event_service = EventService(db_session=db_session)

    criteria = {
        'card_no': request.values.get('card_no', '').strip(),
        'status': request.values.get('status', ''),
        'payment_status': request.values.get('payment_status', '')
    }
    _, item_list = event_service.find_register_primary_by_event_detail_id_and_page(event_detail_id=event_detail_id, criteria=copy(criteria), page=1, row_per_page=999999999)

    register_detail_count_list = []
    register_detail_list = []
    for item in item_list:
        item_detail_list = []
        register_family_total_count, register_family_list = event_service.find_register_family_by_primary_id(primary_id=item['id'])
        register_guest_total_count, register_guest_list = event_service.find_register_guest_by_primary_id(primary_id=item['id'])
        item_detail_list.append(None)
        item_detail_list.extend(register_family_list)
        item_detail_list.extend(register_guest_list)

        total_count = 1 + register_family_total_count + register_guest_total_count
        register_detail_count_list.append(total_count)
        item['sum'] = total_count

        register_detail_list.extend(item_detail_list)

    assert len(item_list) == len(register_detail_count_list)
    assert len(register_detail_list) == sum(register_detail_count_list)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(os.getcwd(), 'private', 'event_register_{}.xlsx'.format(timestamp))

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
    worksheet.set_column(1, 1, 25)  # 會員姓名
    worksheet.set_column(2, 2, 25)  # 會籍編號
    worksheet.set_column(3, 3, 25)  # 會員卡號
    worksheet.set_column(4, 4, 20)  # 報名狀態
    worksheet.set_column(5, 5, 20)  # 繳款狀態
    worksheet.set_column(6, 6, 50)  # 欲扣值順序
    worksheet.set_column(7, 7, 10)  # 人數
    worksheet.set_column(8, 8, 30)  # 建立時間
    worksheet.set_column(9, 9, 30)  # 修改時間
    worksheet.set_column(10, 10, 25)  # 修改人員編號
    worksheet.set_column(11, 11, 25)  # 被邀請人姓名
    worksheet.set_column(12, 12, 30)  # 被邀請人會員卡號
    worksheet.set_column(13, 13, 30)  # 被邀請人報名狀態
    worksheet.set_column(14, 14, 30)  # 被邀請建立時間
    worksheet.set_column(15, 15, 30)  # 被邀請修改時間

    worksheet.write_string(0, 0, '項次', text_format)
    worksheet.write_string(0, 1, '會員姓名', text_format)
    worksheet.write_string(0, 2, '會籍編號', text_format)
    worksheet.write_string(0, 3, '會員卡號', text_format)
    worksheet.write_string(0, 4, '報名狀態', text_format)
    worksheet.write_string(0, 5, '繳款狀態', text_format)
    worksheet.write_string(0, 6, '欲扣值順序', text_format)
    worksheet.write_string(0, 7, '人數', text_format)
    worksheet.write_string(0, 8, '建立時間', text_format)
    worksheet.write_string(0, 9, '修改時間', text_format)
    worksheet.write_string(0, 10, '修改人員編號', text_format)
    worksheet.write_string(0, 11, '被邀請人姓名', text_format)
    worksheet.write_string(0, 12, '被邀請人會員卡號', text_format)
    worksheet.write_string(0, 13, '被邀請人報名狀態', text_format)
    worksheet.write_string(0, 14, '被邀請建立時間', text_format)
    worksheet.write_string(0, 15, '被邀請修改時間', text_format)

    row = 1
    for i, (item, register_detail_count) in enumerate(zip(item_list, register_detail_count_list), start=1):
        payment = f'{Payment[item["payment_1"]].value} > {Payment[item["payment_2"]].value} > {Payment[item["payment_3"]].value}'
        if register_detail_count == 1:
            worksheet.write_string(row, 0, str(i), text_format)
            worksheet.write_string(row, 1, item['name'], text_format)
            worksheet.write_string(row, 2, item['mem_member_no'], text_format)
            worksheet.write_string(row, 3, item['card_no'], text_format)
            worksheet.write_string(row, 4, RegisterStatus[item['status']].value, text_format)
            worksheet.write_string(row, 5, PaymentStatus[item['payment_status']].value, text_format)
            worksheet.write_string(row, 6, payment, text_format)
            worksheet.write_number(row, 7, int(item['sum']), number_format)
            worksheet.write_string(row, 8, item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S'), text_format)
            worksheet.write_string(row, 9, item['update_datetime'].strftime('%Y-%m-%d %H:%M:%S'), text_format)
            if item.get('update_user_id'):
                worksheet.write_string(row, 10, str(item['update_user_id']), text_format)
            else:
                worksheet.write_blank(row, 10, '', clear_format)
            row += 1
        else:
            start = row
            end = start + register_detail_count - 1
            worksheet.merge_range(start, 0, end, 0, str(i), text_format)
            worksheet.merge_range(start, 1, end, 1, item['name'], text_format)
            worksheet.merge_range(start, 2, end, 2, item['mem_member_no'],
                                  text_format)
            worksheet.merge_range(start, 3, end, 3, item['card_no'],
                                  text_format)
            worksheet.merge_range(start, 4, end, 4,
                                  RegisterStatus[item['status']].value,
                                  text_format)
            worksheet.write_string(row, 5, PaymentStatus[item['payment_status']].value, text_format)
            worksheet.merge_range(start, 6, end, 6, payment, text_format)
            worksheet.merge_range(start, 7, end, 7, int(item['sum']), number_format)
            worksheet.merge_range(
                start, 8, end, 8,
                item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                text_format)
            worksheet.merge_range(
                start, 9, end, 9,
                item['update_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                text_format)
            if item.get('update_user_id'):
                worksheet.merge_range(start, 10, end, 10, str(item['update_user_id']), text_format)
            else:
                worksheet.merge_range(start, 10, end, 10, '', clear_format)
            row += register_detail_count

    row = 1
    for item in register_detail_list:
        if not item:
            worksheet.write_blank(row, 11, '', clear_format)
            worksheet.write_blank(row, 12, '', clear_format)
            worksheet.write_blank(row, 13, '', clear_format)
            worksheet.write_blank(row, 14, '', clear_format)
            worksheet.write_blank(row, 15, '', clear_format)
            row += 1
            continue

        if item.get('name'):
            worksheet.write_string(row, 11, item['name'], text_format)
        else:
            worksheet.write_blank(row, 11, '', clear_format)

        if item.get('card_no'):
            worksheet.write_string(row, 12, item['card_no'], text_format)
        else:
            worksheet.write_string(row, 12, '無會籍', text_format)

        if item.get('status'):
            worksheet.write_string(row, 13,
                                   RegisterStatus[item['status']].value,
                                   text_format)
        else:
            worksheet.write_blank(row, 13, '', clear_format)

        if item.get('create_datetime'):
            worksheet.write_string(
                row, 14, item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                text_format)
        else:
            worksheet.write_blank(row, 14, '', clear_format)

        if item.get('update_datetime'):
            worksheet.write_string(
                row, 15, item['update_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                text_format)
        else:
            worksheet.write_blank(row, 15, '', clear_format)

        # if item.get('update_user_id'):
        #     worksheet.write_string(row, 15, str(item['update_user_id']), text_format)
        # else:
        #     worksheet.write_blank(row, 15, '', clear_format)

        row += 1

    workbook.close()
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    response = make_response(
        send_file(
            path,
            mimetype=
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name='活動{}_場次{}_{}.xlsx'.format(primary_id,
                                                     event_detail_id,
                                                     timestamp),
            as_attachment=True))
    response.headers['max-age'] = '0'
    response.headers['Cache-Control'] = 'no-store'
    return response


@user_event_handler.route(
    '/dashboard/user/event/<int:primary_id>/detail/<int:event_detail_id>/register/<int:register_primary_id>/update',
    methods=['GET', 'POST'])
@check_user_login
def register_update(user_id, primary_id, event_detail_id, register_primary_id):
    db_session = g.db_session
    event_service = EventService(db_session=db_session)
    member_service = MemberService(db_session=db_session)

    register_primary = event_service.find_register_primary_by_id(
        primary_id=register_primary_id)
    if not register_primary or register_primary.removed:
        return redirect(
            f'/dashboard/user/event/{primary_id}/detail/{event_detail_id}/register/list'
        )

    # NOTE: my_family_list
    line_info_id = register_primary.line_info_id
    member_id = register_primary.member_id
    card_no = register_primary.card_no
    my_family_list = get_family_list(line_info_id=line_info_id,
                                     member_id=member_id,
                                     card_no=card_no)

    _, register_family_list = event_service.find_register_family_by_primary_id(
        primary_id=register_primary_id)
    _, register_guest_list = event_service.find_register_guest_by_primary_id(
        primary_id=register_primary_id)

    if request.method == 'GET':
        member = member_service.find_member_by_id(register_primary.member_id)

        template_path = 'user/pages/event/event_register_update.html'
        return render_template(template_path,
                               primary_id=primary_id,
                               event_detail_id=event_detail_id,
                               register_primary=register_primary,
                               member=member,
                               my_family_list=my_family_list,
                               register_family_list=register_family_list,
                               register_guest_list=register_guest_list,
                               today=datetime.now().strftime('%Y-%m-%d'))
    """ POST """
    family_list = request.values.get('family_list', '').strip()
    guest_list = request.values.get('guest_list', '').strip()
    family_list = json.loads(family_list)
    guest_list = json.loads(guest_list)

    my_family_card_no_list = []
    if my_family_list:
        my_family_card_no_list = [
            my_family['cardNo'] for my_family in my_family_list
        ]
    family_card_no_list = []
    if family_list:
        family_card_no_list = [
            family.get('cardNo', '').strip() for family in family_list
        ]
    if family_card_no_list:
        for family_card_no in family_card_no_list:
            if family_card_no not in my_family_card_no_list:
                msg = '更新失敗：被邀請人之卡號有誤'
                return redirect(
                    f'/dashboard/user/event/{primary_id}/detail/{event_detail_id}/register/{register_primary_id}/update?result=0&message={msg}'
                )

    remain = event_service.calculate_event_detail_remain(
        detail_id=event_detail_id)
    if register_family_list:
        remain += sum([
            True if register_family.get('status') == RegisterStatus.ACCEPT.name
            else False for register_family in register_family_list
        ])
    if register_guest_list:
        remain += sum([
            True if register_guest.get('status') == RegisterStatus.ACCEPT.name
            else False for register_guest in register_guest_list
        ])

    count = 0
    if family_list:
        count += sum([
            True if family.get('status', RegisterStatus.WAITING.name)
            == RegisterStatus.ACCEPT.name else False for family in family_list
        ])
    if guest_list:
        count += sum([
            True if guest.get('status', RegisterStatus.WAITING.name)
            == RegisterStatus.ACCEPT.name else False for guest in guest_list
        ])

    if remain < count:
        msg = '更新失敗：已達活動人數上限'
        return redirect(
            f'/dashboard/user/event/{primary_id}/detail/{event_detail_id}/register/{register_primary_id}/update?result=0&message={msg}'
        )

    register_family_list_len = len(register_family_list)
    family_list_len = len(family_list)
    if register_family_list_len == family_list_len == 0:
        pass
    elif register_family_list_len >= family_list_len:
        if family_list_len == 0:
            for register_family in register_family_list:
                register_family_id = register_family['id']
                register_family_obj = event_service.find_register_family_by_id(
                    id=register_family_id)
                register_family_obj.delete(update_user_id=user_id)
        else:
            register_family_list_1 = register_family_list[:family_list_len]
            register_family_list_2 = register_family_list[family_list_len:]
            for register_family, family in zip(register_family_list_1,
                                               family_list):
                name = family.get('name', '').strip()
                card_no = family.get('cardNo', '').strip()
                status = family.get('status', '').strip()

                register_family_id = register_family['id']
                register_family_obj = event_service.find_register_family_by_id(
                    id=register_family_id)
                register_family_obj.update(primary_id=register_primary_id,
                                           name=name,
                                           card_no=card_no,
                                           status=status,
                                           update_user_id=user_id)

            if register_family_list_2:
                for register_family in register_family_list_2:
                    register_family_id = register_family['id']
                    register_family_obj = event_service.find_register_family_by_id(
                        id=register_family_id)
                    register_family_obj.delete(update_user_id=user_id)
    elif register_family_list_len < family_list_len:
        if register_family_list_len == 0:
            for family in family_list:
                name = family.get('name', '').strip()
                card_no = family.get('cardNo', '').strip()
                status = family.get('status', '').strip()

                new_register_family = RegisterFamily(
                    primary_id=register_primary_id,
                    name=name,
                    card_no=card_no,
                    status=status)
                db_session.add(new_register_family)
        else:
            family_list_1 = family_list[:register_family_list_len]
            family_list_2 = family_list[register_family_list_len:]
            for register_family, family in zip(register_family_list,
                                               family_list_1):
                name = family.get('name', '').strip()
                card_no = family.get('cardNo', '').strip()
                status = family.get('status', '').strip()

                register_family_id = register_family['id']
                register_family_obj = event_service.find_register_family_by_id(
                    id=register_family_id)
                register_family_obj.update(primary_id=register_primary_id,
                                           name=name,
                                           card_no=card_no,
                                           status=status,
                                           update_user_id=user_id)

            if family_list_2:
                for family in family_list_2:
                    name = family.get('name', '').strip()
                    card_no = family.get('cardNo', '').strip()
                    status = family.get('status', '').strip()

                    new_register_family = RegisterFamily(
                        primary_id=register_primary_id,
                        name=name,
                        card_no=card_no,
                        status=status)
                    db_session.add(new_register_family)

    register_guest_list_len = len(register_guest_list)
    guest_list_len = len(guest_list)
    if register_guest_list_len == guest_list_len == 0:
        pass
    elif register_guest_list_len >= guest_list_len:
        if guest_list_len == 0:
            for register_guest in register_guest_list:
                register_guest_id = register_guest['id']
                register_guest_obj = event_service.find_register_guest_by_id(
                    id=register_guest_id)
                register_guest_obj.delete(update_user_id=user_id)
        else:
            register_guest_list_1 = register_guest_list[:guest_list_len]
            register_guest_list_2 = register_guest_list[guest_list_len:]
            for register_guest, guest in zip(register_guest_list_1,
                                             guest_list):
                name = guest.get('name', '').strip()
                status = guest.get('status', '').strip()

                register_guest_id = register_guest['id']
                register_guest_obj = event_service.find_register_guest_by_id(
                    id=register_guest_id)
                register_guest_obj.update(primary_id=register_primary_id,
                                          name=name,
                                          status=status,
                                          update_user_id=user_id)

            if register_guest_list_2:
                for register_guest in register_guest_list_2:
                    register_guest_id = register_guest['id']
                    register_guest_obj = event_service.find_register_guest_by_id(
                        id=register_guest_id)
                    register_guest_obj.delete(update_user_id=user_id)
    elif register_guest_list_len < guest_list_len:
        if register_guest_list_len == 0:
            for guest in guest_list:
                name = guest.get('name', '').strip()
                status = guest.get('status', '').strip()

                new_register_guest = RegisterGuest(
                    primary_id=register_primary_id, name=name, status=status)
                db_session.add(new_register_guest)
        else:
            guest_list_1 = guest_list[:register_guest_list_len]
            guest_list_2 = guest_list[register_guest_list_len:]
            for register_guest, guest in zip(register_guest_list,
                                             guest_list_1):
                name = guest.get('name', '').strip()
                status = guest.get('status', '').strip()

                register_guest_id = register_guest['id']
                register_guest_obj = event_service.find_register_guest_by_id(
                    id=register_guest_id)
                register_guest_obj.update(primary_id=register_primary_id,
                                          name=name,
                                          status=status,
                                          update_user_id=user_id)

            if guest_list_2:
                for guest in guest_list_2:
                    name = guest.get('name', '').strip()
                    status = guest.get('status', '').strip()

                    new_register_guest = RegisterGuest(
                        primary_id=register_primary_id,
                        name=name,
                        status=status)
                    db_session.add(new_register_guest)

    db_session.commit()
    msg = '更新成功'
    return redirect(
        f'/dashboard/user/event/{primary_id}/detail/{event_detail_id}/register/{register_primary_id}/update?result=1&message={msg}'
    )


@user_event_handler.route('/dashboard/user/event/register/ajax-save-message', methods=['GET', 'POST'])
@check_user_login
def event_register_ajax_send_message_handler(user_id):
    db_session = g.db_session
    event_service = EventService(db_session=db_session)
    member_service = MemberService(db_session=db_session)

    context = request.json
    current_app.logger.info(context)

    message = context.get('message', '').strip()
    if not message:
        return jsonify({'result': 0, 'message': '訊息不得為空'})

    register_primary = event_service.find_register_primary_by_id(primary_id=context['primary_id'])
    if not register_primary:
        return jsonify({'result': 0, 'message': '找不到活動登記資料'})

    content = [{'type': 'TEXT', 'content': message}]

    member_message = MemberMessage()
    member_message.create(card_no=register_primary.card_no, title='活動報名通知', description='', content=json.dumps(content, ensure_ascii=False), event_detail_id=register_primary.event_detail_id)
    db_session.add(member_message)
    db_session.commit()

    try:
        member_line_info = member_service.find_member_line_info_by_id(member_line_info_id=register_primary.line_info_id)
        line_bot_api = LineBotApi(member_line_channel_access_token)
        messages = [TextSendMessage(text=message)]
        line_bot_api.push_message(member_line_info.line_user_id, messages)
    except Exception:
        current_app.logger.error(traceback.format_exc())

    payload = {'result': 1}
    return jsonify(payload)


@user_event_handler.route('/dashboard/user/event/register/ajax-save-batch-message', methods=['GET', 'POST'])
@check_user_login
def event_register_ajax_send_batch_message_handler(user_id):
    """ 批次發送訊息 """
    db_session = g.db_session
    event_service = EventService(db_session=db_session)
    member_service = MemberService(db_session=db_session)

    context = request.json
    current_app.logger.info(context)

    message = context.get('message', '').strip()
    payment_status = context.get('payment_status', '').strip()
    event_detail_id = context.get('event_detail_id', '')
    if not message:
        return jsonify({'result': 0, 'message': '訊息不得為空'})

    if not payment_status:
        return jsonify({'result': 0, 'message': '請選擇付款狀態'})

    if not event_detail_id:
        return jsonify({'result': 0, 'message': '參數錯誤'})

    register_primary_list = event_service.find_register_primary_by_event_detail_id_and_payment_status(event_detail_id=event_detail_id, payment_status=payment_status)
    current_app.logger.info('發送通知至 {} 人'.format(len(register_primary_list)))
    for register_primary in register_primary_list:
        member_message = MemberMessage()
        content = [{'type': 'TEXT', 'content': message}]
        member_message.create(card_no=register_primary.card_no, title='活動報名通知', description='', content=json.dumps(content, ensure_ascii=False), event_detail_id=register_primary.event_detail_id)
        db_session.add(member_message)
        db_session.commit()

        try:
            member_line_info = member_service.find_member_line_info_by_id(member_line_info_id=register_primary.line_info_id)
            line_bot_api = LineBotApi(member_line_channel_access_token)
            messages = [TextSendMessage(text=message)]
            line_bot_api.push_message(member_line_info.line_user_id, messages)
        except Exception:
            current_app.logger.error(traceback.format_exc())

    payload = {'result': 1}
    return jsonify(payload)


@user_event_handler.route('/dashboard/user/event/register/ajax-change-payment-status', methods=['GET', 'POST'])
@check_user_login
def ajax_change_payment_status(user_id):
    db_session = g.db_session
    event_service = EventService(db_session=db_session)

    context = request.json
    current_app.logger.info(context)

    register_primary = event_service.find_register_primary_by_id(primary_id=context['primary_id'])
    if not register_primary:
        return jsonify({'result': 0, 'message': '找不到活動登記資料'})

    register_primary.payment_status = context['payment_status']
    db_session.commit()

    payload = {'result': 1}
    return jsonify(payload)


def get_family_list(line_info_id, member_id, card_no):
    family_list_payload = []
    """ 呼叫德安API查詢 """
    athena_data_context = query_data_by_card_no(card_no=card_no)

    detail_row_context = athena_data_context['ROWSET']['ROW']['DETAIL'][
        'DETAIL_ROW']
    family_row_context = athena_data_context['ROWSET']['ROW']['FAMILY'][
        'FAMILY_ROW'] if athena_data_context['ROWSET']['ROW'][
            'FAMILY'] and 'FAMILY_ROW' in athena_data_context['ROWSET']['ROW'][
                'FAMILY'] else {}

    is_master = detail_row_context.get('IS_MASTER', '').strip()

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
            master_athena_data_context = query_data_by_card_no(
                card_no=family_master_card_no)
            family_detail_row_context = master_athena_data_context['ROWSET'][
                'ROW']['DETAIL']['DETAIL_ROW']
            points = family_detail_row_context.get('VALID_PTS', 0)
            points_expire_date = family_detail_row_context.get(
                'EXPIRE_DAT', '')
            balance = family_detail_row_context.get('BALANCE_AMT', 0)

    family_list_payload_pass_exam = []
    if is_master == 'N':
        # 附卡 只能邀請其他主卡
        for family in family_list_payload:
            if family['isMaster'] == 'Y':
                family_list_payload_pass_exam.append(family)

        family_list_payload = family_list_payload_pass_exam

    return family_list_payload
