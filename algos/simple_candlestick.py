#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.asset_selector import AssetSelector
from src.indicators import Indicators
from util import bullish_sequence, submit_buy_order


def run(alpaca_api):

    # initial trade state
    trading         = False
    trading_symbol  = None
    assets          = AssetSelector(alpaca_api, edgar_token=None).get_assets_by_candlestick_pattern()
    indicators      = Indicators(alpaca_api, assets).get_indicators()

    # trade decision here
    for i in indicators.keys():

        instrument = indicators[i]
        # check if the last three closing prices are a bullish sequence
        if bullish_sequence(instrument["close"].iloc[-3], instrument["close"].iloc[-2], instrument["close"].iloc[-1]):
            # if bullish, check the most recent moving average convergence-divergence
            # has the MACD crossed over its signal and is the MACD percentage change is positive?
            if instrument["macd"].iloc[-1] > instrument["signal"].iloc[-1]:
                # if so, execute a trade
                trading = True
                trading_symbol = str(i)

        if trading_symbol is not None:
            break

    if trading is True:
        # decide how much to buy # TODO

        # then submit
        submit_buy_order(trading_symbol, "buy", "market", "ioc")
