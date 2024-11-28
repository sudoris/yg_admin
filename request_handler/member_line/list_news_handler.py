# -*- coding: utf-8 -*-
import json
from linebot import LineBotApi
from app_config.config import domain, member_line_channel_access_token
from app_model.news_model import NewsStatus
from app_service.news_service import NewsService
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, MemberJoinedEvent, MemberLeftEvent, FollowEvent, UnfollowEvent, TemplateSendMessage,
    ButtonsTemplate, MessageTemplateAction, URITemplateAction, MessageAction, TemplateSendMessage, CarouselTemplate, CarouselColumn,
    QuickReply, QuickReplyButton, ImageSendMessage
)
from app_model.member_model import MemberLineInfo


line_bot_api = LineBotApi(member_line_channel_access_token)


def constrain_int(param):
    """ 把參數固定取回 int """
    try:
        return int(param)
    except Exception as e:
        return 1


def list_news(text, reply_token, line_info:MemberLineInfo, db_session):
    news_service = NewsService(db_session=db_session)

    page = 1
    if '-' in text:
        page = text.split('-')[1]
    page = int(page)

    criteria = {'status': 'NORMAL'}
    if not line_info:
        criteria['flag_visitor'] = 1
    else:
        if line_info.member_id:
            criteria['flag_member'] = 1
        else:
            criteria['flag_visitor'] = 1

    total_count, item_list = news_service.find_news_by_criteria(criteria=criteria, page=page, row_per_page=9, order_by='display_date')

    if len(item_list) == 0:
        # line_bot_api.reply_message(reply_token, TextSendMessage(text='目前暫時沒有資料'))
        return

    column_list = []
    for item in item_list:
        thumbnail = domain + item['cover_image'] if item['cover_image'] else domain + '/static/general/images/default_news_cover.jpg'
        column = CarouselColumn(
            thumbnail_image_url=thumbnail,
            title=item['title'],
            text=item['description'],
            actions=[
                MessageTemplateAction(
                    label='查看詳細',
                    text= item['line_keyword'] if item['line_keyword'] else '#消息內容-{}'.format(item['id'])
                ),
            ]
        )
        column_list.append(column)

    if total_count > page * 9:
        column = CarouselColumn(
            thumbnail_image_url= domain + '/static/general/images/default_news_cover.jpg',
            title='更多',
            text='點選查看更多訊息',
            actions=[
                MessageTemplateAction(
                    label='更多訊息',
                    text= '最新消息-{}'.format(page + 1)
                ),
            ]
        )
        column_list.append(column)

    carousel_template = TemplateSendMessage(
        alt_text='訊息列表',
        template=CarouselTemplate(
            columns=column_list
        )
    )
    line_bot_api.reply_message(reply_token, carousel_template)


def news_detail(text, reply_token, line_info, db_session, flag_other):
    service = NewsService(db_session=db_session)

    news = None
    if '-' in text:
        news_id = constrain_int(text.split('-')[1])
        news = service.find_news_by_id(news_id)

    if not news:
        news = service.find_news_by_line_keyword(line_keyword=text)

    if flag_other and not news:
        return

    if not news or news.removed or news.status != NewsStatus.NORMAL:
        # line_bot_api.reply_message(reply_token, TextSendMessage(text='目前暫時沒有資料'))
        return

    fragment_list = json.loads(news.content)
    if len(fragment_list) == 0:
        # line_bot_api.reply_message(reply_token, TextSendMessage(text='目前暫時沒有資料'))
        return

    messages = []
    for fragment in fragment_list:
        if fragment['type'] == 'TEXT':
            messages.append(TextSendMessage(text=fragment['content']))
        if fragment['type'] == 'IMAGE':
            url = domain + fragment['content']
            messages.append(ImageSendMessage(url, url))

    line_bot_api.reply_message(reply_token, messages=messages)
