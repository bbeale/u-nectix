#!/usr/bin/env python
# -*- coding: utf-8 -*-
from algos import BaseAlgo
from src.asset_selector import AssetSelector, AssetValidationException
from broker import BrokerException
from util import time_from_datetime
from lib.portfolio_manager import PortfolioManager
import os


class Algorithm(AssetSelector, BaseAlgo):

    def __init__(self, broker, cli_args):
        super().__init__(broker=broker, cli_args=cli_args, edgar_token=None)

    def get_ratings(self, algo_time=None, window_size=5):
        pass

    def portfolio_allocation(self, data, cash):
        pass

    def total_asset_value(self, positions, date):
        pass


def run(broker, args):

    if not broker or broker is None:
        raise BrokerException('[!] A broker instance is required.')

    """Trade example ganked from https://github.com/alpacahq/example-portfolio-manager and implemented here."""
    manager = PortfolioManager(broker.api)
    # Hedging SPY with GLD 1:1
    manager.add_items([
        ['SPY', 0.5],
        ['GLD', 0.5],
    ])
    manager.percent_rebalance('block')
