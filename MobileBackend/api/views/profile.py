# -*- coding: utf-8 -*-

import logging

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import ObjectDoesNotExist

from ...common.wrapper import check_body, check_user_login
from ...common.utils import body_extract, mills_timestamp, init_http_response_my_enum, make_json_response
from ...common.choices import RespCode, AccountStatus
from ...account.models import Account
from ...api.dto.dto import UpdateProfileDTO

logger = logging.getLogger('django')


@require_http_methods(['POST', 'GET'])
@check_user_login
def profile_router(request, *args, **kwargs):
    if request.method == 'POST':
        return update_profile(request, *args, **kwargs)
    elif request.method == 'GET':
        return get_profile(request, *args, **kwargs)


def get_profile(request, *args, **kwargs):

    account_id = kwargs.get('account_id')

    try:
        account = Account.objects.get(account_id=account_id, status=AccountStatus.valid.key)
    except ObjectDoesNotExist as e:
        logger.info("Get Profile: %s" % e)
        resp = init_http_response_my_enum(RespCode.server_error)
        return make_json_response(resp=resp)

    data = dict(
        account_id=account_id,
        nickname=account.nickname,
        avatar=account.avatar_url,
        major=account.major,
        school=account.school,
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


@check_body
def update_profile(request, body, *args, **kwargs):

    update_profile_dto = UpdateProfileDTO()
    body_extract(body, update_profile_dto)
    timestamp = mills_timestamp()
    account_id = kwargs.get('account_id')

    try:
        account = Account.objects.get(account_id=account_id, status=AccountStatus.valid.key)
    except ObjectDoesNotExist as e:
        logger.info("Update Profile: %s" % e)
        resp = init_http_response_my_enum(RespCode.server_error)
        return make_json_response(HttpResponse, resp)

    if update_profile_dto.nickname:
        account.nickname = update_profile_dto.nickname
    if update_profile_dto.major:
        account.major = update_profile_dto.major
    if update_profile_dto.school:
        account.school = update_profile_dto.school
    if update_profile_dto.avatar:
        account.avatar_url = update_profile_dto.avatar
    if update_profile_dto.new_password:
        account.password = update_profile_dto.password_md5
    account.update_date = timestamp
    account.save()

    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)




