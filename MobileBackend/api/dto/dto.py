# -*- coding: utf-8 -*-

import hashlib

from ...common.config import SALT
from ...common.utils import email_validate


class LoginAndRegisterDTO(object):

    def __init__(self):
        self.email = None
        self.password = None

    @property
    def password_md5(self):
        return hashlib.sha3_256((self.password + SALT).encode()).hexdigest()

    @property
    def is_empty(self):
        return not self.email or not self.password

    @property
    def invalid_email(self):
        return not email_validate(self.email)


class ValidateDTO(object):

    def __init__(self):
        self.email = None
        self.code = None
        self.password = None

    @property
    def is_empty(self):
        return not self.email or not self.code

    @property
    def password_md5(self):
        return hashlib.sha3_256((self.password + SALT).encode()).hexdigest()


class UpdateProfileDTO(object):

    def __init__(self):
        self.nickname = None
        self.avatar = None
        self.major = None
        self.new_password = None

    @property
    def password_md5(self):
        return hashlib.sha3_256((self.new_password + SALT).encode()).hexdigest()


class FriendApplyDTO(object):

    def __init__(self):
        self.friend_id = None
        self.message = None

    @property
    def is_empty(self):
        return not self.friend_id or not self.message


class FriendActionDTO(object):

    def __init__(self):
        self.request_id = None
        self.action = None

    @property
    def is_empty(self):
        return not self.request_id or not self.action


class LocationDTO(object):

    def __init__(self):
        self.x = None
        self.y = None
        self.name = None

    @property
    def is_empty(self):
        return not self.x or not self.y or not self.name


class EventDTO(object):

    def __init__(self):
        self.topic = None
        self.description = None
        self.location = LocationDTO()
        self.event_time = None

    @property
    def is_empty(self):
        return not self.topic or not self.description or not self.event_time or self.location.is_empty


