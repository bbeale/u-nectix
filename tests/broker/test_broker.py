#!/usr/bin/env python
# -*- coding: utf-8 -*-
from broker.broker import Broker
from util import parse_configs, time_from_timestamp
from alpaca_trade_api.rest import REST
from broker.broker import Broker
from unittest import TestCase
import alpaca_trade_api.entity as Ent
import time
import os


class TestBroker(TestCase):

    config = parse_configs(path=os.path.join('../../', 'config.ini'))
    alpaca = REST(base_url=config['alpaca']['APCA_API_BASE_URL'], key_id=config['alpaca']['APCA_API_KEY_ID'],
                secret_key=config['alpaca']['APCA_API_SECRET_KEY'], api_version=config['alpaca']['VERSION'])
    broker = Broker(alpaca)

    def test_get_account(self):

        res = TestBroker.broker.get_account()
        self.assertIsInstance(res, Ent.Account)

    def test_get_clock(self):

        res = TestBroker.broker.get_clock()
        self.assertIsInstance(res, Ent.Clock)

    def test_get_calendar(self):
        start = time_from_timestamp(time.time() - (604800 * 54))
        end = time_from_timestamp(time.time())
        res = TestBroker.broker.get_calendar(start_date=start, end_date=end)
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], Ent.Calendar)

    def test_get_assets(self):

        res = TestBroker.broker.get_assets()
        print('[] ')

    def test_get_asset(self):

        res = TestBroker.broker.get_asset()
        print('[] ')

    def test_get_positions(self):

        res = TestBroker.broker.get_positions()
        print('[] ')

    def test_get_position(self):

        res = TestBroker.broker.get_position()
        print('[] ')

    def test_close_all_positions(self):

        res = TestBroker.broker.close_all_positions()
        print('[] ')

    def test_close_position(self):

        res = TestBroker.broker.close_position()
        print('[] ')

    def test_get_orders(self):

        res = TestBroker.broker.get_orders()
        print('[] ')

    def test_get_order(self):

        res = TestBroker.broker.get_order()
        print('[] ')

    def test_submit_order(self):

        res = TestBroker.broker.submit_order()
        print('[] ')

    def test_replace_order(self):

        res = TestBroker.broker.replace_order()
        print('[] ')

    def cancel_all_orders(self):

        res = TestBroker.broker.cancel_all_orders()
        print('[] ')

    def test_cancel_order(self):

        res = TestBroker.broker.cancel_order()
        print('[] ')

    def test_get_asset_df(self):

        res = TestBroker.broker.get_asset_df()
        print('[] ')

    def test_get_watchlists(self):

        res = TestBroker.broker.get_watchlists()
        print('[] ')

    def test_get_watchlist(self):

        res = TestBroker.broker.get_watchlist()
        print('[] ')

    def test_add_watchlist(self):

        res = TestBroker.broker.add_watchlist()
        print('[] ')

    def test_add_to_watchlist(self):

        res = TestBroker.broker.add_to_watchlist()
        print('[] ')

    def test_clear_watchlist(self):

        res = TestBroker.broker.clear_watchlist()
        print('[] ')

    def test_calculate_tolerable_risk(self):

        res = TestBroker.broker.calculate_tolerable_risk()
        print('[] ')

    def test_calculate_position_size(self):

        res = TestBroker.broker.calculate_position_size()
        print('[] ')
