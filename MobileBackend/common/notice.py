# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger('django')


class NoticeManager(object):

    def __init__(self):
        self.notice_map = dict()

    def set_notice(self, account_id: int, key, content):
        logger.info('[NoticeManager] From: {} To: {} Content: {}'.format(key, account_id, str(content)))
        if account_id not in self.notice_map:
            self.notice_map[account_id] = dict()
        notice = self.notice_map[account_id]
        notice[key] = content

    def get_notice(self, account_id: int):
        if account_id not in self.notice_map:
            return None
        notice = self.notice_map.get(account_id)
        if len(notice) > 0:
            return notice

    def remove_notice(self, account_id: int, key: int):
        if account_id not in self.notice_map:
            return
        notice = self.notice_map.get(account_id)
        notice.pop(key)


friend_apply_notice = NoticeManager()
friend_list_notice = NoticeManager()
