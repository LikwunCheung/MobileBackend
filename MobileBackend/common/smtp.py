# -*- coding: utf-8 -*-

import logging
import threading

from queue import Queue
from smtplib import SMTP
from email.mime.text import MIMEText
from email.header import Header

from django.db.models import ObjectDoesNotExist
from django.db.utils import OperationalError
from django.db.transaction import atomic

from .utils import mills_timestamp
from .choices import AccountStatus, Status, SendEmailAction
from .config import *
from ..account.models import RegisterRecord, Account, ForgetPassword

logger = logging.getLogger('django')
connector = None
connected = False


def init_smtp():
    global connected, connector

    try:
        try:
            logger.info(u'[SMTP] Connecting Google SMTP Service: ' + GMAIL_ADDRESS + ':' + str(GMAIL_PORT))
            connector = SMTP(host=GMAIL_ADDRESS, port=GMAIL_PORT, timeout=3)
            connector.ehlo()
            connector.starttls()
            connector.login(GMAIL_ACCOUNT, GMAIL_PASSWORD)
        except Exception as e:
            logger.error('[SMTP] Connect Fail: ', e)
            return
        connector.set_debuglevel(1)
        connected = True
        logger.info(u'[SMTP] Connecting Google SMTP Service Success!')
    except Exception as e:
        logger.error('[SMTP] Connect Fail: ', e)


def send_email(title: str, address: str, content: str):
    global connected, connector

    if not connected or not isinstance(connector, SMTP):
        return False

    try:
        logger.info(u'[SMTP] Sending Email: %s %s' % (address, content))

        message = MIMEText(content, PLAIN, UTF8)
        message[FROM] = Header(VALIDATE_SENDER, UTF8)
        message[SENDER] = Header(VALIDATE_SENDER, UTF8)
        message[TO] = Header(address, UTF8)
        message[SUBJECT] = Header(title, UTF8)

        init_smtp()
        connector.sendmail(GMAIL_ACCOUNT, address, message.as_string())
        connector.quit()
        return True
    except Exception as e:
        logger.info('SMTP Disconnected: ', e)
        init_smtp()
        return False


class SendEmailPool(threading.Thread):

    def __init__(self, size=128):
        self.count = 0
        self.size = size
        self.pool = Queue(self.size)
        super(SendEmailPool, self).__init__()

    def put_task(self, action, account_id, record_id, address, content):
        logger.info(u'[SMTP] Receive: %d %d %d %s' % (action, account_id, record_id, address))

        self.pool.put(dict(
            action=action,
            account_id=account_id,
            record_id=record_id,
            email=address,
            text=content,
        ))

    def consume(self):
        task = self.pool.get(block=True, timeout=None)
        action = SendEmailAction(task['action'])

        if action == SendEmailAction.register:

            logger.info(u'[SMTP] Send Register Email: %d %s' % (self.count, str(task)))
            try:
                record = RegisterRecord.objects.get(record_id=task['record_id'], status=Status.valid.key)
                account = Account.objects.get(account_id=task['account_id'], status__lt=AccountStatus.valid.key)
            except ObjectDoesNotExist as e:
                logger.info('[SMTP] %s' % e)
                return
            except OperationalError as e:
                logger.info('[SMTP] %s' % e)
                self.pool.put(task)
                return

            if record.expired <= mills_timestamp():
                timestamp = mills_timestamp()
                with atomic():
                    account.status = AccountStatus.expired.key
                    account.update_date = timestamp
                    record.status = Status.invalid.key
                    record.update_date = timestamp
                    account.save()
                    record.save()
                return

            if send_email(VALIDATE_TITLE, task['email'], task['text']):
                account.status = AccountStatus.wait_accept.key
                account.update_date = mills_timestamp()
                account.save()
            else:
                self.pool.put(task)

        elif action == SendEmailAction.forget:

            logger.info(u'[SMTP] Send Forget Email: %d %s' % (self.count, str(task)))
            try:
                record = ForgetPassword.objects.get(record_id=task['record_id'], status=Status.valid.key)
            except ObjectDoesNotExist as e:
                logger.info('[SMTP] %s' % e)
                return
            except OperationalError as e:
                logger.info('[SMTP] %s' % e)
                self.pool.put(task)
                return

            if record.expired <= mills_timestamp():
                record.status = Status.invalid.key
                record.update_date = mills_timestamp()
                record.save()
                return

            if not send_email(FORGET_TITLE, task['email'], task['text']):
                self.pool.put(task)

    def run(self):
        while True:
            self.count += 1
            self.consume()
