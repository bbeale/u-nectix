#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pykrakenapi.pykrakenapi import KrakenAPIError
from src.broker import BrokerValidationException
import pandas as pd
import time


class KrakDealer:

    def __init__(self, api):
        self.api = api
        self.trading_account = self.get_account()
        self.trade_balance = self.get_trade_balance()
        self.trading_blocked = True if self.trade_balance["tb"] == float(0) else False

    def get_account(self):
        return self.api.get_account_balance()

    def get_trade_balance(self, asset="XBT"):
        return self.api.get_trade_balance(asset=asset)
