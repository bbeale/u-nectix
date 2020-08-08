#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from datetime import datetime
from pytz import timezone
import time
import util


class TestUtil(TestCase):

    def test_time_from_timestamp(self):
        ts = time.time()
        res = util.time_from_timestamp(time_stamp=ts)
        self.assertIsInstance(res, str)

    def test_time_from_datetime(self):
        dt = datetime.now(timezone('EST'))
        res = util.time_from_datetime(dt=dt)
        self.assertIsInstance(res, str)

    def test_bullish_sequence(self):
        seq = [33, 22, 11]
        res = util.bullish_sequence(*seq)
        self.assertTrue(res)

    def test_long_bullish_sequence(self):
        seq = [55, 44, 33, 22, 11]
        res = util.long_bullish_sequence(*seq)
        self.assertTrue(res)

    def test_get_returns(self):
        prices = None
        res = util.get_returns(prices=prices)
        self.assertIsInstance(res, int)

    def test_num_bars(self):
        barset = None
        length = 5
        res = util.num_bars(barset=barset, length=length)
        self.assertIsInstance(res, int)

    def test_logarithmic_scale(self):
        series = None
        res = util.logarithmic_scale(series=series)
        self.assertIsInstance(res, int)
