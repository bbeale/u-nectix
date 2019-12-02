#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.asset_selector import AssetSelector
from src.indicators import Indicators
from util import bullish_sequence, submit_order, time_formatter
import time

def run(alpaca_api):

    # initial trade state
    trading         = False
    trading_symbol  = None
    assets          = AssetSelector(alpaca_api, edgar_token=None).bullish_candlesticks(64, 1)
    indicators      = Indicators(alpaca_api, assets).get_all_asset_indicators(backdate=time_formatter(time.time() - (604800 * 54)))

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

    # debug
    print("[?] Trading: ", trading is True)
    if trading is True:
        # decide how much to buy # TODO
        quant = 10

        # then submit a buy order
        submit_order(
            api_reference=alpaca_api,
            ticker=trading_symbol,
            qty=quant,
            transaction_side="buy",
            ttype="market",
            time_in_force="ioc"
        )
