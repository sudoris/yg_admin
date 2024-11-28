# -*- coding: utf-8 -*-
from app_config.config_env import env
from dotenv import load_dotenv
load_dotenv('.env')

import logging
from app_config.config import secret_key
from datetime import timedelta
from flask import Flask, session, send_from_directory, g
from app_model.initialization_database import get_db_session

# Core
from request_handler.core.core_scan_handler import core_scan_handler

# Member Line
from request_handler.member_line.member_line_web_hook_handler import member_line_web_hook_handler

# User
from request_handler.user.user_login_handler import user_login_handler
from request_handler.user.user_index_handler import user_index_handler
from request_handler.user.user_account_handler import user_account_handler
from request_handler.user.user_line_user_handler import user_line_user_handler
from request_handler.user.user_news_handler import user_news_handler
from request_handler.user.user_event_handler import user_event_handler
from request_handler.user.user_product_handler import user_product_handler
from request_handler.user.user_product_order_handler import user_product_order_handler
from request_handler.user.user_banner_handler import user_banner_handler
from request_handler.user.user_member_handler import user_member_handler
from request_handler.user.user_member_card_handler import user_member_card_handler
from request_handler.user.user_log_handler import user_log_handler
from request_handler.user.user_rich_menu_handler import user_rich_menu_handler


# API
from request_handler.api.v1.v1_api_banner_handler import v1_api_banner_handler
from request_handler.api.v1.v1_api_product_handler import v1_api_product_handler
from request_handler.api.v1.v1_api_product_order_handler import v1_api_product_order_handler
from request_handler.api.v1.v1_api_event_handler import v1_api_event_handler
from request_handler.api.v1.v1_api_event_register_handler import v1_api_event_register_handler
from request_handler.api.v1.v1_api_member_handler import v1_api_member_handler
from request_handler.api.v1.v1_api_member_login_handler import v1_api_member_login_handler
from request_handler.api.v1.v1_api_member_register_handler import v1_api_member_register_handler
from request_handler.api.v1.v1_api_message_handler import v1_api_message_handler


app = Flask(__name__, template_folder='template')

app.secret_key = secret_key
app.logger.setLevel(logging.INFO)
app.url_map.strict_slashes = False
if env != 'app':
    app.debug = True


@app.before_request
def make_session_permanent():
    # Ref: https://stackoverflow.com/questions/11783025/is-there-an-easy-way-to-make-sessions-timeout-in-flask/11785722
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=180)


@app.before_request
def register_db_session():
    db_session = get_db_session()
    g.db_session = db_session


@app.teardown_appcontext
def app_context_teardown_event(exception=None):
    if hasattr(g, 'db_session'):
        g.db_session.close()


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/public/<path:path>')
def send_public(path):
    return send_from_directory('public', path)


@app.route('/upload_public/<path:path>')
def send_upload_public(path):
    return send_from_directory('upload_public', path)


@app.template_filter('build_params')
def build_params(criteria):
    """ Jinja2中 使用的自訂 function """
    if not isinstance(criteria, dict):
        raise Exception('Criteria Must Be a Dict')
    url = ""
    for key, value in criteria.items():
        url += "{}={}&".format(key, value if value else '')
    return url


@app.template_filter('percent')
def jinja2_filter_percent(numerator, denominator):
    """ Jinja2中 使用的自訂 function """
    if not denominator:
        return 0
    return int((numerator/denominator) * 100 * 2.5)

# Core
app.register_blueprint(core_scan_handler)

# Member Line
app.register_blueprint(member_line_web_hook_handler)

# User
app.register_blueprint(user_login_handler)
app.register_blueprint(user_index_handler)
app.register_blueprint(user_account_handler)
app.register_blueprint(user_line_user_handler)
app.register_blueprint(user_news_handler)
app.register_blueprint(user_event_handler)
app.register_blueprint(user_product_handler)
app.register_blueprint(user_product_order_handler)
app.register_blueprint(user_banner_handler)
app.register_blueprint(user_member_handler)
app.register_blueprint(user_member_card_handler)
app.register_blueprint(user_rich_menu_handler)


# API
app.register_blueprint(v1_api_banner_handler)
app.register_blueprint(v1_api_product_handler)
app.register_blueprint(v1_api_product_order_handler)
app.register_blueprint(v1_api_event_handler)
app.register_blueprint(v1_api_event_register_handler)
app.register_blueprint(v1_api_member_handler)
app.register_blueprint(v1_api_member_login_handler)
app.register_blueprint(v1_api_message_handler)
app.register_blueprint(v1_api_member_register_handler)
app.register_blueprint(user_log_handler)


if __name__ == '__main__':
    app.run()
