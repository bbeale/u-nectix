#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.asset_selector import AssetSelector
from src.indicators import Indicators
from util import submit_buy_order


def run(alpaca_api):

    # initial trade state
    trading_symbol  = None
    trading         = False
    # assets          = AssetSelector(alpaca_api, edgar_token=None).bullish_candlesticks()
    assets          = AssetSelector(alpaca_api, edgar_token=None).bearish_candlesticks()
    indicators      = Indicators(alpaca_api, assets).get_cluster()

    # trade decision here
    for i in indicators.keys():     # TODO: make AssetSelector return more stocks to cycle through

        instrument = indicators[i]
        # check the most recent moving average convergence-divergence
        # has the MACD crossed over its signal and is the MACD percentage change is positive?
        if instrument["macd"].iloc[-1] > instrument["signal"].iloc[-1] and instrument["macd_ptc"].iloc[-1] > 0:
            # if the MACD checks out, check the directional movement indicator
            # has the DMI positive value crossed over the negative value?
            if instrument["DMp"].iloc[-1] > instrument["DMm"].iloc[-1]:
                # if DMI checks out, check the volume zone oscillator
                # the VZO should be in the bottom half of the bullish range
                if 5 < instrument["vzo"].iloc[-1] <= 40:
                    # bullish DMI trend range is 5 to 40
                    trading = True
                    trading_symbol = str(i)

        if trading_symbol is not None:
            break

    # debugging line that forces the trade to not be made
    print("Trading is True: ", trading is True)
    trading = False
    if trading is True:
        # decide how much to buy # TODO

        # then submit
        submit_buy_order(trading_symbol, "buy", "market", "ioc")
