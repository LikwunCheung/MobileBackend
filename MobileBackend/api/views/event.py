# -*- coding: utf-8 -*-

import logging

from django.views.decorators.http import require_http_methods
from django.db.models import ObjectDoesNotExist
from django.db import transaction

from ...api.dto.dto import FriendApplyDTO, FriendActionDTO
from ...account.models import Account
from ...event.models import Event, EventParticipate
from ...common.utils import body_extract, mills_timestamp, init_http_response_my_enum, make_json_response
from ...common.wrapper import check_body, check_user_login
from ...common.choices import RespCode, FriendApplyStatus, Status, AccountStatus, FriendApplyAction
from ...common.config import *
from ...common.notice import friend_apply_notice, friend_list_notice

logger = logging.getLogger('django')


@require_http_methods(['POST', 'GET'])
@check_user_login
def event_router(request, *args, **kwargs):
    event_id = kwargs.get('id', None)
    if request.method == 'POST':
        if event_id:
            return update_event(request, *args, **kwargs)
        return create_event(request, *args, **kwargs)
    elif request.method == 'GET':
        if event_id:
            return get_event_detail(request, event_id, *args, **kwargs)
        return get_event_list(request, *args, **kwargs)


@check_body
def create_event(request, body, *args, **kwargs):
    pass


@check_body
def update_event(request, body, *args, **kwargs):
    pass


def get_event_list(request, *args, **kwargs):
    pass


def get_event_detail(request, event_id, *args, **kwargs):
    pass


@require_http_methods(['GET'])
@check_user_login
def event_explore(request, *args, **kwargs):
    pass


@require_http_methods(['POST'])
@check_user_login
@check_body
def join_event(request, body, *args, **kwargs):
    pass


@require_http_methods(['POST'])
@check_user_login
@check_body
def remove_event(request, body, *args, **kwargs):
    pass
