# -*- coding: utf-8 -*-

import logging

from django.views.decorators.http import require_http_methods
from django.db.models import ObjectDoesNotExist
from django.db import transaction

from ...api.dto.dto import EventDTO
from ...account.models import Account
from ...friend.models import SocialRelation
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
    account_id = kwargs['account_id']
    event_dto = EventDTO()
    body_extract(body, event_dto)
    timestamp = mills_timestamp()

    if event_dto.is_empty:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    if event_dto.event_time <= timestamp:
        resp = init_http_response_my_enum(RespCode.expired)
        return make_json_response(resp=resp)

    try:
        new_event = Event(account_id=account_id, topic=event_dto.topic, description=event_dto.description,
                          location_x=event_dto.location.x, location_y=event_dto.location.y,
                          location_name=event_dto.location.name, event_date=event_dto.event_time,
                          status=Status.valid.key, create_date=timestamp, update_date=timestamp)
        new_event.save()

        new_join_event = EventParticipate(account_id=account_id, event_id=new_event.event_id, status=Status.valid.key,
                                          create_date=timestamp, update_date=timestamp)
        new_join_event.save()
    except Exception as e:
        print(e)
        resp = init_http_response_my_enum(RespCode.server_error)
        return make_json_response(resp=resp)

    data = dict(
        event_id=new_event.event_id,
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


@check_body
def update_event(request, body, *args, **kwargs):
    account_id = kwargs['account_id']
    event_id = kwargs['id']
    event_dto = EventDTO()
    body_extract(body, event_dto)

    try:
        exist_event = Event.objects.get(event_id=event_id, account_id=account_id, status=Status.valid.key)
    except ObjectDoesNotExist as e:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    if event_dto.topic:
        exist_event.topic = event_dto.topic
    if event_dto.description:
        exist_event.description = event_dto.description
    if event_dto.event_time:
        exist_event.event_date = event_dto.event_time
    if event_dto.location.x:
        exist_event.location_x = event_dto.location.x
    if event_dto.location.y:
        exist_event.location_y = event_dto.location.y
    if event_dto.location.name:
        exist_event.location_name = event_dto.location.name
    exist_event.update_date = mills_timestamp()
    exist_event.save()

    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)


def get_event_list(request, *args, **kwargs):
    account_id = kwargs['account_id']
    offset = int(request.GET.get('offset', 0))
    size = int(request.GET.get('size', 20))

    joined_event = EventParticipate.objects.filter(account_id=account_id, status=Status.valid.key).only('event_id')

    event_ids = [joined.event_id for joined in joined_event]
    events = Event.objects.filter(event_id__in=event_ids, status=Status.valid.key)\
        .order_by('event_date', 'event_id')[offset: offset + size + 1]

    has_more = 0
    if len(events) > size:
        has_more = 1
        events = events[:size]

    host_ids = [event.account_id for event in events]
    accounts = Account.objects.filter(account_id__in=host_ids, status=AccountStatus.valid.key)
    friends = SocialRelation.objects.filter(account_id=account_id, friend_id__in=host_ids, status=Status.valid.key)\
        .only('friend_id')

    account_map = dict()
    for account in accounts:
        account_map[account.account_id] = account
    friend_ids = set([friend.friend_id for friend in friends])
    friend_ids.add(account_id)

    data = dict(
        event=[dict(
            event_id=e.event_id,
            topic=e.topic,
            description=e.description,
            create_time=e.create_date,
            event_time=e.event_date,
            location=dict(
                x=e.location_x,
                y=e.location_y,
                name=e.location_name,
            ),
            host=dict(
                avatar=account_map[e.account_id].avatar_url,
                nickname=account_map[e.account_id].nickname,
                account_id=e.account_id,
                is_friend=1 if e.account_id in friend_ids else 0,
            ),
        ) for e in events],
        offset=offset + len(events),
        has_more=has_more,
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


def get_event_detail(request, event_id, *args, **kwargs):

    account_id = kwargs['account_id']

    try:
        existed_event = Event.objects.get(event_id=event_id, status=Status.valid.key)
    except ObjectDoesNotExist as e:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    joined_event = EventParticipate.objects.filter(event_id=event_id, status=Status.valid.key).only('account_id')
    account_ids = [joined.account_id for joined in joined_event]

    accounts = Account.objects.filter(account_id__in=account_ids, status=AccountStatus.valid.key)

    friends = SocialRelation.objects.filter(account_id=account_id, friend_id__in=account_ids, status=Status.valid.key)\
        .only('friend_id')
    friend_ids = set([friend.friend_id for friend in friends])
    friend_ids.add(account_id)

    account_map = dict()
    for account in accounts:
        account_map[account.account_id] = account

    data = dict(
        event_id=existed_event.event_id,
        topic=existed_event.topic,
        description=existed_event.description,
        event_time=existed_event.event_date,
        create_time=existed_event.create_date,
        location=dict(
            x=existed_event.location_x,
            y=existed_event.location_y,
            name=existed_event.location_name,
        ),
        host=dict(
            avatar=account_map[existed_event.account_id].avatar_url,
            nickname=account_map[existed_event.account_id].nickname,
            account_id=existed_event.account_id,
            is_friend=1 if existed_event.account_id in friend_ids else 0,
        ),
        paticipate=[dict(
            avatar=account_map[joined.account_id].avatar_url,
            nickname=account_map[joined.account_id].nickname,
            account_id=joined.account_id,
            is_friend=1 if joined.account_id in friend_ids else 0,
        ) for joined in joined_event],
        total_participate=len(joined_event),
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


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
def quit_event(request, body, *args, **kwargs):
    pass


@require_http_methods(['GET', 'POST'])
@check_user_login
def comment_router(request, *args, **kwargs):
    event_id = kwargs.get('id', None)
    if request.method == 'POST':
        return create_comment(request, event_id, *args, **kwargs)
    elif request.method == 'GET':
        return get_comment(request, event_id, *args, **kwargs)


def create_comment(request, event_id, *args, **kwargs):
    pass


def get_comment(request, event_id, *args, **kwargs):
    pass


@require_http_methods(['POST'])
@check_user_login
@check_body
def remove_comment(request, body, *args, **kwargs):
    pass
