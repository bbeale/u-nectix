#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.broker.broker import BrokerValidationException


class ForexBroker:

    def __init__(self, api, pair):

        if not api or api is None:
            raise BrokerValidationException('[!] API instance required.')

        if not pair or pair is None:
            raise BrokerValidationException('[!] Trading instrument required.')

        self.api = api
        self.pair = pair
        self.trading_account = self.get_account()
        self.trade_balance = self.get_trade_balance(asset=self.pair)
        self.trading_blocked = self.is_trading_blocked()

    def get_account(self):
        raise NotImplementedError

    def get_trade_balance(self, asset):
        raise NotImplementedError

    def is_trading_blocked(self):
        return True if self.trade_balance <= 0 else False
