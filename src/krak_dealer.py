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
        self.pairs = [p for p in self.trading_account.axes]

    def get_server_time(self):
        """Get the current time from the Kraken server.

        :return:
        """
        try:
            result = self.api.get_server_time()
        except KrakenAPIError as error:
            raise error
        else:
            return result

    def get_account(self):
        """Get our trading account.

        :return:
        """
        try:
            result = self.api.get_account_balance()
        except KrakenAPIError as error:
            raise error
        else:
            return result

    def get_trade_balance(self, asset):
        """Get the available trading balance of an asset.

        :param asset:
        :return:
        """
        if not asset or asset is None:
            raise BrokerValidationException("[!] Invalid asset.")

        try:
            result = self.api.get_trade_balance(asset=asset)
        except KrakenAPIError as error:
            raise error
        else:
            return result

    def get_tradable_asset_pairs(self, info=None, pair=None):
        """Get a list of tradeable asset pairs.

        :param info:
        :param pair:
        :return:
        """
        try:
            result = self.api.get_tradable_asset_pairs(info=info, pair=pair)
        except KrakenAPIError as error:
            raise error
        else:
            return result

    def get_ticker_information(self, pair):
        """Get recent ticker info for a given asset pair.

        :param pair:
        :return:
        """
        if not pair or pair is None:
            raise BrokerValidationException("[!] Invalid asset pair.")

        try:
            result = self.api.get_ticker_information(pair=pair)
        except KrakenAPIError as error:
            raise error
        else:
            return result

    def get_ohlc_data(self, pair, interval=1, since=None, ascending=False):
        """Get an OHLC formatted data frame for a given asset pair.

        :param pair:
        :param interval:
        :param since:
        :param ascending:
        :return:
        """
        if not pair or pair is None:
            raise BrokerValidationException("[!] Invalid asset pair.")

        try:
            result = self.api.get_ohlc_data(pair, interval=interval, since=since, ascending=ascending)
        except KrakenAPIError as error:
            raise error
        else:
            return result

    def get_order_book(self, pair, count=100, ascending=False):
        """Get the order book for a given asset pair.

        :param pair:
        :param count:
        :param ascending:
        :return:
        """
        if not pair or pair is None:
            raise BrokerValidationException("[!] Invalid asset pair.")

        try:
            result = self.api.get_order_book(pair, count, ascending)
        except KrakenAPIError as error:
            raise error
        else:
            return result

    def get_recent_spread_data(self, pair, since=None, ascending=False):
        """Get recent spread data for a given asset pair.

        :param pair:
        :param since:
        :param ascending:
        :return:
        """
        if not pair or pair is None:
            raise BrokerValidationException("[!] Invalid asset pair.")

        try:
            result = self.api.get_recent_spread_data(pair, since, ascending)
        except KrakenAPIError as error:
            raise error
        else:
            return result
