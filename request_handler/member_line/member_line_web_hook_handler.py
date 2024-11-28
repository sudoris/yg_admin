# -*- coding: utf-8 -*-
import re
from app_config.config import member_line_channel_secret, member_line_channel_access_token
from linebot import LineBotApi, WebhookHandler
from flask import Blueprint, request, redirect, make_response, session, json, current_app, jsonify, abort, g
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage
from request_handler.member_line.list_news_handler import news_detail, list_news
from app_service.member_service import MemberService


member_line_web_hook_handler = Blueprint('member_line_web_hook_handler', __name__)


line_bot_api = LineBotApi(member_line_channel_access_token)
handler = WebhookHandler(member_line_channel_secret)


@member_line_web_hook_handler.route("/member/line/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    current_app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    db_session = g.db_session
    member_service = MemberService(db_session=db_session)

    line_user_id = event.source.user_id
    text = event.message.text.strip()
    reply_token = event.reply_token

    member_line_info = member_service.find_member_line_info_by_line_user_id(line_user_id=line_user_id)


    if re.match(r'^最新消息-\d+$', text) or text == '最新消息':
        list_news(text, reply_token, member_line_info, db_session)
    elif re.match(r'^消息內容-\d+$', text):
        """ 新聞詳細 """
        news_detail(text, reply_token, None, db_session, False)
    else:
        """ 新聞詳細, 有設定關鍵字 """
        news_detail(text, reply_token, None, db_session, True)
