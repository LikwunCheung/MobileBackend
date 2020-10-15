# -*- coding: utf-8 -*-

import logging

from django.views.decorators.http import require_http_methods
from django.db.models import ObjectDoesNotExist
from django.db import transaction

from ...api.dto.dto import FriendApplyDTO, FriendActionDTO
from ...account.models import Account
from ...friend.models import SocialApply, SocialRelation
from ...common.utils import body_extract, mills_timestamp, init_http_response_my_enum, make_json_response
from ...common.wrapper import check_body, check_user_login
from ...common.choices import RespCode, FriendApplyStatus, Status, AccountStatus, FriendApplyAction
from ...common.config import *
from ...common.notice import friend_apply_notice, friend_list_notice


logger = logging.getLogger('django')


@require_http_methods(['POST', 'GET'])
@check_user_login
def friend_router(request, *args, **kwargs):
    if request.method == 'POST':
        return new_friend_apply(request, *args, **kwargs)
    elif request.method == 'GET':
        return get_friend_list(request, *args, **kwargs)


def get_friend_list(request, *args, **kwargs):

    account_id = kwargs.get(ACCOUNT_ID)
    relations = SocialRelation.objects.filter(account_id=account_id, status=Status.valid.key)
    friend = list()

    if len(relations):
        friend_ids = [relation.friend_id for relation in relations]
        friends = Account.objects.filter(account_id__in=friend_ids, status=AccountStatus.valid.key).order_by('nickname')
        friend = [dict(
            account_id=f.account_id,
            nickname=f.nickname,
            avatar=f.avatar_url,
        ) for f in friends]
    data = dict(
        friend=friend,
        total_count=len(relations),
    )

    # Remove the notice of friend list
    notice = friend_list_notice.get_notice(account_id)
    if notice and notice.get('flag', None):
        friend_list_notice.remove_notice(account_id, 'flag')

    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


@check_body
def new_friend_apply(request, body, *args, **kwargs):

    account_id = kwargs.get(ACCOUNT_ID)
    apply_dto = FriendApplyDTO()
    body_extract(body, apply_dto)
    timestamp = mills_timestamp()

    if apply_dto.is_empty or apply_dto.friend_id == account_id:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    if SocialRelation.objects.filter(account_id=account_id, friend_id=apply_dto.friend_id, status=Status.valid.key).exists():
        resp = init_http_response_my_enum(RespCode.existed_application)
        return make_json_response(resp=resp)

    try:
        existed_apply = SocialApply.objects.get(account_id=account_id, target_id=apply_dto.friend_id,
                                                status__lte=FriendApplyStatus.wait_accept.key)
        if existed_apply.expired <= timestamp:
            existed_apply.status = FriendApplyStatus.reject.key
            existed_apply.update_date = timestamp
            existed_apply.save()

            resp = init_http_response_my_enum(RespCode.expired)
            return make_json_response(resp=resp)

        resp = init_http_response_my_enum(RespCode.existed_application)
        return make_json_response(resp=resp)
    except ObjectDoesNotExist as e:
        pass

    expired = timestamp + FRIEND_APPLY_EXPIRED
    apply = SocialApply(account_id=account_id, target_id=apply_dto.friend_id, message=apply_dto.message,
                        status=FriendApplyStatus.wait_accept.key, create_date=timestamp, update_date=timestamp,
                        expired=expired)
    account = Account.objects.get(account_id=account_id, status=AccountStatus.valid.key)

    apply_content = dict(
        account_id=account_id,
        nickname=account.nickname,
        avatar=account.avatar_url,
        message=apply_dto.message,
        timestamp=timestamp,
    )
    with transaction.atomic():
        apply.save()
        apply_content['request_id'] = apply.apply_id
        friend_apply_notice.set_notice(apply_dto.friend_id, account_id, apply_content)

    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)


@require_http_methods(['GET'])
@check_user_login
def search_friend(request, *args, **kwargs):

    account_id = kwargs.get(ACCOUNT_ID)
    email = request.GET.get('email', None)
    nickname = request.GET.get('nickname', None)

    if not email and not nickname:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    search_accounts = list()
    if email:
        search_accounts = Account.objects.filter(email__istartswith=email, status=AccountStatus.valid.key).order_by('email')
    elif nickname:
        search_accounts = Account.objects.filter(nickname__istartswith=nickname, status=AccountStatus.valid.key)\
            .order_by('nickname')

    search_ids = [account.account_id for account in search_accounts]
    relations = SocialRelation.objects.filter(account_id=account_id, friend_id__in=search_ids, status=Status.valid.key)
    relation_ids = set([relation.friend_id for relation in relations])

    result = list()
    for search_account in search_accounts:
        if search_account.account_id != account_id:
            result.append(dict(
                account_id=search_account.account_id,
                email=search_account.email,
                nickname=search_account.nickname,
                avatar=search_account.avatar_url,
                is_friend=1 if search_account.account_id in relation_ids else 0,
            ))

    data = dict(
        result=result,
        total_count=len(result),
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


@require_http_methods(['GET'])
@check_user_login
def friend_notice(request, *args, **kwargs):

    account_id = kwargs.get(ACCOUNT_ID)
    apply_notices = friend_apply_notice.get_notice(account_id)
    list_notices = friend_list_notice.get_notice(account_id)

    print(apply_notices)
    print(list_notices)

    friend_list_updated = 0
    if list_notices and dict(list_notices).get('flag', None):
        friend_list_updated = 1

    data = dict(
        friend_list_updated=friend_list_updated,
        request=list(apply_notices.values()) if apply_notices else None,
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


@require_http_methods(['POST'])
@check_user_login
@check_body
def friend_accept(request, body, *args, **kwargs):

    account_id = kwargs.get(ACCOUNT_ID)
    accept_dto = FriendActionDTO()
    body_extract(body, accept_dto)

    if accept_dto.is_empty:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    try:
        apply = SocialApply.objects.get(apply_id=accept_dto.request_id, status=FriendApplyStatus.wait_accept.key)
    except ObjectDoesNotExist as e:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    timestamp = mills_timestamp()
    if apply.expired <= timestamp:
        apply.status = FriendApplyStatus.reject.key
        apply.update_date = timestamp
        apply.save()
        resp = init_http_response_my_enum(RespCode.expired)
        return make_json_response(resp=resp)

    action = FriendApplyAction(int(accept_dto.action))
    if action == FriendApplyAction.accept:
        apply.status = FriendApplyStatus.accept.key
        apply.update_date = timestamp

        with transaction.atomic():
            friend_list_notice.set_notice(account_id, 'flag', 1)
            friend_list_notice.set_notice(apply.account_id, 'flag', 1)

            SocialRelation(account_id=account_id, friend_id=apply.account_id, status=Status.valid.key,
                           update_date=timestamp, create_date=timestamp).save()
            SocialRelation(account_id=apply.account_id, friend_id=account_id, status=Status.valid.key,
                           update_date=timestamp, create_date=timestamp).save()
            apply.save()
    elif action == FriendApplyAction.reject:
        apply.status = FriendApplyStatus.reject.key
        apply.update_date = timestamp
        apply.save()

    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)


@require_http_methods(['POST'])
@check_user_login
@check_body
def remove_friend(request, body, *args, **kwargs):

    account_id = kwargs['account_id']
    friend_id = body.get('friend_id', None)
    if not friend_id:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    try:
        timestamp = mills_timestamp()
        friend_from = SocialRelation.objects.get(account_id=account_id, friend_id=friend_id, status=Status.valid.key)
        friend_to = SocialRelation.objects.get(account_id=friend_id, friend_id=account_id, status=Status.valid.key)

        friend_from.update_date = timestamp
        friend_from.status = Status.invalid.key
        friend_to.update_date = timestamp
        friend_to.status = Status.invalid.key

        with transaction.atomic():
            friend_from.save()
            friend_to.save()

        friend_list_notice.set_notice(account_id, 'flag', 1)
        friend_list_notice.set_notice(friend_id, 'flag', 1)
    except ObjectDoesNotExist as e:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)


