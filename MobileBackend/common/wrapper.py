# -*- coding: utf-8 -*-

import ujson
import json
import logging

from .token import token_manager
from .utils import init_http_response_my_enum, make_json_response
from .choices import RespCode

logger = logging.getLogger('django')


def check_body(func):
    """

    :param func:
    :return:
    """

    def wrapper(request, *args, **kwargs):
        try:
            body = dict(ujson.loads(request.body))
            logger.info(body)
        except ValueError or json.JSONDecodeError as e:
            logger.info(request.body)
            resp = init_http_response_my_enum(RespCode.incorrect_body)
            return make_json_response(resp=resp)

        return func(request, body, *args, **kwargs)

    return wrapper


def check_user_login(func):
    """
    Disable for testing
    :param func:
    :return:
    """

    def wrapper(request, *args, **kwargs):
        token = request.META.get('HTTP_X_MY_TOKEN', None)
        account_id = token_manager.get_token(token)
        if not account_id:
            resp = init_http_response_my_enum(RespCode.need_login)
            return make_json_response(resp=resp)

        kwargs['account_id'] = account_id
        return func(request, *args, **kwargs)

    return wrapper
