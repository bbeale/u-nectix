#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import parse_configs, parse_args
from alpaca_trade_api.rest import REST
from src.asset_selector import AssetSelector
from src.broker import Broker, BrokerException
from unittest import TestCase
import os


class TestAssetSelector(TestCase):

    config = parse_configs(path=os.path.join("../../", "config.ini"))
    args = parse_args()
    if args.mode is None:
        args.mode = 'long'
    if args.period is None:
        args.period = "1D"
    if args.algorithm is None:
        args.algorithm = "bullish_volume_overnight_hold"
    if args.testperiods is None:
        args.testperiods = 30
    if args.max is None:
        args.max = 26
    if args.min is None:
        args.min = 6

    alpaca = REST(base_url=config["alpaca"]["APCA_API_BASE_URL"], key_id=config["alpaca"]["APCA_API_KEY_ID"],
                secret_key=config["alpaca"]["APCA_API_SECRET_KEY"], api_version=config["alpaca"]["VERSION"])
    broker = Broker(alpaca)
    selector = AssetSelector(broker, cli_args=args)

    def test_top_gainer_efficient_frontier(self):
        result = self.selector.top_gainer_efficient_frontier()
        self.assertIsNotNone(result)
        print("...")
