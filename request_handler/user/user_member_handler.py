# -*- coding: utf-8 -*-
from copy import copy
from flask import Blueprint, request, redirect, make_response, session, json, current_app, jsonify, send_file, g
from request_handler.user.user_request_helper import check_user_login, render_template
from app_service.member_service import MemberService
from app_utility.athena_utility import query_data_by_card_no, get_member_card_list_by_identify_no


row_per_page = 10
user_member_handler = Blueprint('user_member_handler', __name__)


@user_member_handler.route('/dashboard/user/member/list', methods=['GET', 'POST'])
@user_member_handler.route('/dashboard/user/member/list/<int:page>', methods=['GET', 'POST'])
@check_user_login
def member_list(user_id, page=1):
    db_session = g.db_session
    member_service = MemberService(db_session=db_session)

    criteria = {
        'name': request.values.get('name', ''),
        'identify_no': request.values.get('identify_no', ''),
        'no': request.values.get('no', '')
    }
    total_count, item_list = member_service.find_member_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)

    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    template_path = 'user/pages/member/member_list.html'
    return render_template(template_path, item_list=item_list, total_page=total_page, page=page, criteria=criteria)


@user_member_handler.route('/dashboard/user/member/detail/<int:member_id>', methods=['GET', 'POST'])
@check_user_login
def member_detail(user_id, member_id):

    db_session = g.db_session
    member_service = MemberService(db_session=db_session)

    member = member_service.find_member_by_id(member_id=member_id)
    if not member:
        return redirect('/dashboard/user/member/list')

    card_list = get_member_card_list_by_identify_no(member.identify_no)
    if not card_list:
        return redirect('/dashboard/user/member/list')

    if request.method == 'GET':
        card_no = card_list[0]['cardNo']

        """ 呼叫德安API查詢 """
        athena_data_context = query_data_by_card_no(card_no=card_no)
        current_app.logger.info(athena_data_context)

        detail_row_context = athena_data_context['ROWSET']['ROW']['DETAIL']['DETAIL_ROW']

        no = detail_row_context.get('MEMBER_COD', '').strip()
        name = detail_row_context.get('ALT_NAM', '').strip()
        points = detail_row_context.get('VALID_PTS', 0)
        points_expire_date = detail_row_context.get('EXPIRE_DAT', '')
        balance = detail_row_context.get('BALANCE_AMT', 0)

        member.no = no
        member.name = name
        db_session.commit()

        total_interest = member.interest_1 + member.interest_2 + member.interest_3 + member.interest_4 + member.interest_5 + member.interest_6 + member.interest_7 + member.interest_8 + member.interest_9 + member.interest_10
        if total_interest == 0:
            total_interest = 100

        member_line_info = member_service.find_last_member_line_info_by_member_id(member_id=member_id)
        template_path = 'user/pages/member/member_detail.html'
        return render_template(template_path, member=member, member_line_info=member_line_info, card_list=card_list,
                               total_interest=total_interest, points=points, points_expire_date=points_expire_date, balance=balance)

    """ POST """
    remark = request.values.get('remark', '')
    member.remark = remark
    db_session.commit()

    return redirect('/dashboard/user/member/detail/{}'.format(member_id))



