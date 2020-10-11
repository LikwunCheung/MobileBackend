# -*- coding: utf-8 -*-

import logging

from django.views.decorators.http import require_http_methods
from django.db.models import ObjectDoesNotExist
from django.db import transaction

from ...api.dto.dto import LoginAndRegisterDTO, ValidateDTO
from ...account.models import Account, RegisterRecord, ForgetPassword
from ...common import smtp_thread
from ...common.utils import body_extract, mills_timestamp, init_http_response_my_enum, make_json_response, \
    get_validate_code
from ...common.wrapper import check_body, check_user_login
from ...common.token import token_manager
from ...common.choices import RespCode, AccountStatus, Status, SendEmailAction
from ...common.config import *

logger = logging.getLogger('django')


@require_http_methods(['POST'])
@check_body
def login(request, body, *args, **kwargs):
    """
    Login

    :param request:
    :param body:
    :param args:
    :param kwargs:
    :return:
    """

    login_dto = LoginAndRegisterDTO()
    body_extract(body, login_dto)

    if login_dto.is_empty or login_dto.invalid_email:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    try:
        account = Account.objects.get(email=login_dto.email, password=login_dto.password_md5,
                                      status=AccountStatus.valid.key)
    except ObjectDoesNotExist as e:
        resp = init_http_response_my_enum(RespCode.login_fail)
        return make_json_response(resp=resp)
    token = token_manager.set_token(account.account_id)

    data = dict(
        account_id=account.account_id,
        nickname=account.nickname,
        major=account.major,
        avatar=account.avatar_url,
        token=token,
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


@require_http_methods(['POST'])
@check_user_login
def logout(request, *args, **kwargs):
    """
    Logout

    :param request:
    :param args:
    :param kwargs:
    :return:
    """

    account_id = request.POST.get('account_id')
    token_manager.remove_token(account_id)

    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)


@require_http_methods(['POST'])
@check_body
def register(request, body, *args, **kwargs):
    """
    Register

    :param request:
    :param body:
    :param args:
    :param kwargs:
    :return:
    """

    register_dto = LoginAndRegisterDTO()
    body_extract(body, register_dto)
    timestamp = mills_timestamp()

    if register_dto.is_empty or register_dto.invalid_email:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    """
    Check if the user register record expired, and if the user already existed
    """
    existed_account = Account.objects.filter(email=register_dto.email, status__lte=AccountStatus.valid.key).first()
    if existed_account is not None:
        if existed_account.status == AccountStatus.valid.key:
            resp = init_http_response_my_enum(RespCode.account_existed)
            return make_json_response(resp=resp)

        existed_record = RegisterRecord.objects\
            .filter(account_id=existed_account.account_id, status=Status.valid.key).first()

        if existed_record is None:
            resp = init_http_response_my_enum(RespCode.server_error)
            return make_json_response(resp=resp)

        if existed_record.expired <= timestamp:
            logger.info('Registration Expired: %s' % existed_account)
            with transaction.atomic():
                existed_record.status = Status.invalid.key
                existed_record.update_date = timestamp
                existed_account.status = AccountStatus.expired.key
                existed_account.update_date = timestamp
                existed_record.save()
                existed_account.save()
        else:
            if existed_account.update_date + VALIDATE_EXPIRED / 10 < timestamp:
                logger.info('Resend Validation Email: %s' % existed_account)
                content = str(VALIDATE_TEMPLATE).replace(PATTERN_NICKNAME, existed_account.nickname)\
                    .replace(PATTERN_CODE, str(existed_record.code))
                smtp_thread.put_task(SendEmailAction.REGISTER.value, existed_account.account_id,
                                     existed_record.record_id, existed_account.email, content)
            resp = init_http_response_my_enum(RespCode.resend_email)
            return make_json_response(resp=resp)

    expired = timestamp + VALIDATE_EXPIRED  # 15min
    code = get_validate_code()
    nickname = DEFAULT_NICKNAME + str(get_validate_code(10))

    try:
        with transaction.atomic():
            account = Account(email=register_dto.email, password=register_dto.password_md5, avatar_url=DEFAULT_AVATAR,
                              nickname=nickname, major=DEFAULT_MAJOR, status=AccountStatus.created.key,
                              create_date=timestamp, update_date=timestamp)
            account.save()

            record = RegisterRecord(account_id=account.account_id, code=code, expired=expired, status=Status.valid.key,
                                    create_date=timestamp, update_date=timestamp)
            record.save()
    except Exception as e:
        logger.error(e)
        resp = init_http_response_my_enum(RespCode.server_error)
        return make_json_response(resp=resp)

    content = str(VALIDATE_TEMPLATE).replace(PATTERN_NICKNAME, nickname).replace(PATTERN_CODE, str(record.code))
    smtp_thread.put_task(SendEmailAction.REGISTER.value, account.account_id, record.record_id, account.email, content)

    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)


@require_http_methods(['POST'])
@check_body
def validate(request, body, *args, **kwargs):

    validate_dto = ValidateDTO()
    body_extract(body, validate_dto)

    if validate_dto.is_empty:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    code = int(validate_dto.code)
    timestamp = mills_timestamp()

    try:
        account = Account.objects.get(email=validate_dto.email, status=AccountStatus.wait_accept.key)
        record = RegisterRecord.objects.get(account_id=account.account_id, code=code, status=Status.valid.key)

        if record.expired <= timestamp:
            with transaction.atomic():
                record.status = Status.invalid.key
                record.update_date = timestamp
                account.status = AccountStatus.expired.key
                account.update_date = timestamp
                record.save()
                account.save()

            resp = init_http_response_my_enum(RespCode.expired)
            return make_json_response(resp=resp)
    except ObjectDoesNotExist as e:
        logger.info('Validate Error: %s' % e)
        resp = init_http_response_my_enum(RespCode.validate_fail)
        return make_json_response(resp=resp)

    with transaction.atomic():
        record.status = Status.invalid.key
        record.update_date = timestamp
        account.status = AccountStatus.valid.key
        account.update_date = timestamp
        account.save()
        record.save()

    data = dict(
        account_id=account.account_id,
        token=token_manager.set_token(account.account_id),
        nickname=account.nickname,
        major=account.major,
        avatar=account.avatar_url,
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


@require_http_methods(['POST'])
@check_body
def forget_password(request, body, *args, **kwargs):

    email = body['email']

    try:
        account = Account.objects.get(email=email, status=AccountStatus.valid.key)
    except ObjectDoesNotExist as e:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    existed_forget = ForgetPassword.objects.filter(account_id=account.account_id, status=Status.valid.key).first()
    if existed_forget:
        existed_forget.status = Status.invalid.key
        existed_forget.save()

    code = get_validate_code()
    timestamp = mills_timestamp()
    expired = timestamp + FORGET_EXPIRED
    forget = ForgetPassword(account_id=account.account_id, code=code, expired=expired, status=Status.valid.key,
                            create_date=timestamp, update_date=timestamp)
    forget.save()

    content = str(FORGET_TEMPLATE).replace(PATTERN_NICKNAME, account.nickname).replace(PATTERN_CODE, str(forget.code))
    smtp_thread.put_task(SendEmailAction.FORGET.value, account.account_id, forget.record_id, account.email, content)

    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)


@require_http_methods(['POST'])
@check_body
def forget_validate(request, body, *args, **kwargs):

    validate_dto = ValidateDTO()
    body_extract(body, validate_dto)

    if validate_dto.is_empty:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    code = int(validate_dto.code)
    timestamp = mills_timestamp()

    try:
        account = Account.objects.get(email=validate_dto.email, status=AccountStatus.valid.key)
        record = ForgetPassword.objects.get(account_id=account.account_id, code=code, status=Status.valid.key)

        if record.expired <= timestamp:
            with transaction.atomic():
                record.status = Status.invalid.key
                record.update_date = timestamp
                record.save()

            resp = init_http_response_my_enum(RespCode.expired)
            return make_json_response(resp=resp)

        record.status = Status.invalid.key
        record.update_date = timestamp
        record.save()

    except ObjectDoesNotExist as e:
        logger.info('Validate Error: %s' % e)
        resp = init_http_response_my_enum(RespCode.validate_fail)
        return make_json_response(resp=resp)

    data = dict(
        account_id=account.account_id,
        token=token_manager.set_token(account.account_id),
        nickname=account.nickname,
        major=account.major,
        avatar=account.avatar_url,
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)

