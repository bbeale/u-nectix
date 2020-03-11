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
    krak_deaker = KrakDealer(kraken, "XRPUSD")

    def test_get_account(self):
        account = self.krak_deaker.get_account()
        print(account)