# -*- coding: utf-8 -*-

from .utils import generate_token, mills_timestamp
from .config import TOKEN_REFRESH


class Token(object):

    def __init__(self, account_id):
        self.account_id = account_id
        self.expired = None
        self.refresh()

    def refresh(self):
        self.expired = mills_timestamp() + TOKEN_REFRESH  # 1day


class TokenManager(object):

    def __init__(self):
        self.token_dict = dict()
        self.account_dict = dict()

    def set_token(self, account_id: int):

        # Check if the account existed
        token = self.account_dict.get(account_id, None)
        if token:
            token_info = self.token_dict.get(token)
            token_info.refresh()
            return token

        token = generate_token()
        self.token_dict[token] = Token(account_id)
        self.account_dict[account_id] = token
        return token

    def get_token(self, token: str):
        token_info = self.token_dict.get(token, None)
        if not token_info or token_info.expired <= mills_timestamp():
            return None

        token_info.refresh()
        return token_info.account_id

    def remove_token(self, account_id: int):
        token = self.account_dict.get(account_id, None)

        if not token:
            return

        self.account_dict.pop(account_id)
        self.token_dict.pop(token)
        return


token_manager = TokenManager()
