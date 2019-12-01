#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.asset_selector import AssetSelector
from src.indicators import Indicators
from util import submit_buy_order, time_formatter
import time

def run(alpaca_api):

    # initial trade state
    trading_symbol  = None
    trading         = False
    assets          = AssetSelector(alpaca_api, edgar_token=None).bullish_candlesticks(64, 1)
    indicators      = Indicators(alpaca_api, assets).get_all_asset_indicators(backdate=time_formatter(time.time() - (604800 * 54)))

    # trade decision here
    for i in indicators.keys():

        instrument = indicators[i]

        # do the processing for machine learning and see which one (if any) to trade
        # TODO: implement machine learning

        if trading_symbol is not None:
            break

    # debugging line that forces the trade to not be made
    print("Trading: ", trading is True)
    trading = False
    if trading is True:
        # decide how much to buy # TODO
        quant = 10

        # then submit
        submit_buy_order(trading_symbol, quant, "buy", "market", time_in_force="ioc")
