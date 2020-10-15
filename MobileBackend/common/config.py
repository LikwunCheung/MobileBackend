# -*- coding: utf-8 -*-

SESSION_REFRESH = 30 * 60
SINGLE_PAGE_LIMIT = 20

SALT = 'Zsl2&(91bsd%^sa1LD'

UTF8 = 'utf-8'
PLAIN = 'plain'
FROM = 'From'
TO = 'To'
SENDER = 'Sender'
SUBJECT = 'Subject'

PATTERN_NICKNAME = '<NICKNAME>'
PATTERN_CODE = '<CODE>'

GMAIL_ADDRESS = 'smtp.gmail.com'
GMAIL_PORT = 587
GMAIL_ACCOUNT = 'swen90013.2020.sp@gmail.com'
GMAIL_PASSWORD = 'fvwdissshcpobsdl'

VALIDATE_TEMPLATE = 'Dear <NICKNAME>,\n\n' \
                    'Welcome to join CampusEvent!\n' \
                    'Please enter the following verification code to verify your email within 15 minutes!\n\n' \
                    '<CODE>\n\n' \
                    'Regards,\n' \
                    'CampusEvent Support Team\n'
VALIDATE_SENDER = 'CampusEvent'
VALIDATE_TITLE = '[CampusEvent] Verify Your Email Address'
VALIDATE_EXPIRED = 1000 * 60 * 15

FORGET_TEMPLATE = 'Dear <NICKNAME>,\n\n' \
                  'You are applying to reset your password\n' \
                  'Please enter the following verification code to reset your password within 5 minutes!\n\n' \
                  '<CODE>\n\n' \
                  'Regards,\n' \
                  'CampusEvent Support Team\n'
FORGET_TITLE = '[CampusEvent] Reset Password'
FORGET_EXPIRED = 1000 * 60 * 5

DEFAULT_AVATAR = '37cKxzwdSrF3YWlGC0PKEUrs'
DEFAULT_NICKNAME = 'User'
DEFAULT_MAJOR = 'Unknown'

TOKEN_REFRESH = 1000 * 60 * 60 * 3
FRIEND_APPLY_EXPIRED = 1000 * 60 * 60 * 24

ACCOUNT_ID = 'account_id'

