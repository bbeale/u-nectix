#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pykrakenapi.pykrakenapi import KrakenAPI
from src.krak_dealer import KrakDealer
from util import parse_configs
from unittest import TestCase
import krakenex


class TestKrakDealer(TestCase):

    config = parse_configs("../../config.ini")
    api = krakenex.API(key=config["kraken"]["api_key"], secret=config["kraken"]["private_key"])
    kraken = KrakenAPI(api, tier="Starter")
    krak_deaker = KrakDealer(kraken)
    asset = "XXRP"
    pair = "XXRPXXBT"

    def test_get_server_time(self):
        servertime = self.krak_deaker.get_server_time()
        print(servertime)

    def test_get_account(self):
        account = self.krak_deaker.get_account()
        print(account)

    def test_get_trade_balance(self):
        bal = self.krak_deaker.get_trade_balance(asset=self.asset)
        print(bal)

    def test_get_tradable_asset_pairs(self):
        pairs = self.krak_deaker.get_tradable_asset_pairs()
        print(pairs)

    def test_get_ticker_information(self):
        info = self.krak_deaker.get_ticker_information(pair=self.pair)
        print(info)

    def test_get_ohlc_data(self):
        ohlc = self.krak_deaker.get_ohlc_data(pair=self.pair)
        print(ohlc)

    def test_get_order_book(self):
        orderbook = self.krak_deaker.get_order_book(pair=self.pair)
        print(orderbook)

    def test_get_recent_spread_data(self):
        spread = self.krak_deaker.get_recent_spread_data(pair=self.pair)
        print(spread)
