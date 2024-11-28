# -*- coding: utf-8 -*-
from app_config.config import (
    domain
)
from flask import Blueprint, jsonify, g
from app_service.banner_service import BannerService


v1_api_banner_handler = Blueprint('v1_api_banner_handler', __name__)


@v1_api_banner_handler.route('/api/v1/product/banner/list', methods=['GET', 'POST'])
def product_banner_list():
    db_session = g.db_session
    banner_service = BannerService(db_session=db_session)

    item_list = banner_service.find_active_banner()
    banner_payload = []
    for item in item_list:
        banner_payload.append({
            'id': item['id'],
            'image_url': domain + item['image_url'],
            'url': item['url'] if item['url'] else '#'
        })

    payload = {
        'result': 1,
        'data': {
            'items': banner_payload
        }
    }
    return jsonify(payload)

