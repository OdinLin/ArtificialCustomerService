# -*- coding:utf-8 -*-
import functools
from flask import session, jsonify, g
from datetime import timedelta
from flask import make_response, request, current_app, jsonify
from functools import update_wrapper
from functools import wraps
import time

def login_required(view_func):
    """登录验证装饰器"""
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户的登录状态
        user_id = session.get("user_id")
        if user_id is not None:
            # 将user_id保存到g对象中，方便视图函数直接使用
            g.user_id = user_id

            # 如果用户已登录，执行视图函数
            return view_func(*args, **kwargs)
        else:
            # 如果用户未登录，返回json数据，告知前端
            return jsonify(errcode="404", errmsg="用户未登录")

    return wrapper
    # @functools.wraps(view_func)
    # def wrapper(*args, **kwargs):
    #
    #         # 将user_id保存到g对象中，方便视图函数直接使用
    #     g.user_id = 1
    #
    #     # 如果用户已登录，执行视图函数
    #     return view_func(*args, **kwargs)
    # return wrapper


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()

        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                if isinstance(f(*args, **kwargs), dict):
                    resp = make_response(jsonify(f(*args, **kwargs)))
                else:
                    resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def crossmain(origin=None):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            func = f(*args, **kwargs)
            if isinstance(f(*args, **kwargs), dict):
                func = jsonify(func)
            else:
                func = f(func)
            resp = make_response(func)
            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            return resp
        return update_wrapper(wrapped_function, f)
    return decorator