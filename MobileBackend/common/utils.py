# -*- coding: utf-8 -*-

import logging
import ujson
import time
import random
import string
import re

from django.http.response import HttpResponse

from MobileBackend.common.choices import MyEnum

logger = logging.getLogger('django')


def make_json_response(func=HttpResponse, resp=None):
    return func(ujson.dumps(resp), content_type='application/json')


def make_redirect_response(func=HttpResponse, resp=None):
    return func(ujson.dumps(resp), content_type='application/json', status=302)


def init_http_response(code, message, data=None):
    return dict(
        code=code,
        message=message,
        data=data,
    )


def init_http_response_my_enum(resp: MyEnum, data: dict = None):
    return init_http_response(resp.key, resp.msg, data)


def body_extract(body: dict, obj: object):
    """
    Extract parameters from the request body
    :param body:
    :param obj:
    :return:
    """
    for i in obj.__dict__.keys():
        if i in body:
            obj.__setattr__(i, body.get(i))


def mills_timestamp():
    return int(time.time() * 1000)


def email_validate(email):
    return re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email)


def generate_token(length: int = 4):
    return ''.join([''.join(random.sample(string.ascii_letters + string.digits, 8)) for i in range(length)])


def get_validate_code(size: int = 6):
    return int(''.join(random.sample(string.digits, size)))


def file_iterator(file_path, chunk_size=512):
    with open(file_path, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break