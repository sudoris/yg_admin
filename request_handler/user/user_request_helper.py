# -*- coding: utf-8 -*-
from typing import List
from functools import wraps
from flask import request, session, redirect, get_flashed_messages
from flask import render_template as flask_render_template


def render_template(template_path, **kwargs):
    context = {
        'error_list': get_flashed_messages(category_filter=["error"]),
        'success_list': get_flashed_messages(category_filter=["success"])}
    context.update(kwargs)
    return flask_render_template(template_path, **context)


def check_user_login(func):
    """ 檢查 User 是否登入 """
    @wraps(func)
    def wrapped(*args, **kwargs):
        user_id = session.get('user_id', None)
        if not user_id:
            return redirect('/dashboard/user')

        return func(user_id=user_id, *args, **kwargs)

    return wrapped


def check_user_privilege(allow_privilege_id_list: List):
    """
    檢查 User權限
    Ref: https://stackoverflow.com/a/42581103
    """
    def real_decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            user_privilege_id_list = session.get('user_privilege_id_list', [])
            flag_pass = False
            for user_privilege_id in user_privilege_id_list:
                if user_privilege_id in allow_privilege_id_list:
                    flag_pass = True

            if not flag_pass:
                return redirect('/dashboard/user/index')

            return func(*args, **kwargs)
        return wrapped
    return real_decorator
