# -*- coding: utf-8 -*-
import json
import requests
from flask import current_app


class LineUtility:

    @staticmethod
    def verify_id_token(id_token, channel_id):
        """
        驗證 Line Id Token
        Ref: https://developers.line.biz/en/reference/social-api/#verify-id-token
        """
        url = 'https://api.line.me/oauth2/v2.1/verify?client_id={}&id_token={}'.format(channel_id, id_token)
        current_app.logger.info(url)

        response = requests.post(url)
        current_app.logger.info(response.text)
        context = json.loads(response.text)

        line_user_id = context['sub']
        email = context.get('email', '')
        return line_user_id, email
