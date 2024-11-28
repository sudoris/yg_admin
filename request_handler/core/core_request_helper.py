# -*- coding: utf-8 -*-
from flask import request, current_app, session, redirect, g


def get_real_ip():
    if request.headers.get('HTTP_CF_CONNECTING_IP'):
        return request.headers['HTTP_CF_CONNECTING_IP']
    elif request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For']
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


def constrain_int(param):
    """ 把參數固定取回 int """
    try:
        return int(param)
    except Exception as e:
        return 1
