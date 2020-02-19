#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.indicator_collection import Indicators as Indicators
from src.asset_selector import AssetSelector
from src.broker import BrokerException
from util import time_formatter
import time


def run(broker, args):

    if not broker or broker is None:
        raise BrokerException("[!] A broker instance is required.")
    else:
        broker = broker

    # initial trade state
    trading_symbol  = None
    trading         = False
    # backdate        = time_formatter(time.time() - (604800 * 54))
    asset_selector  = AssetSelector(broker, args, edgar_token=None)
    # tickers         = asset_selector.bullish_candlesticks()
    indicators      = Indicators(broker, args, asset_selector).data

    # trade decision here
    for i in indicators.keys():

        instrument = indicators[i]

        # do the processing for machine learning and see which one (if any) to trade
        # TODO: implement machine learning
        print("[debug] Instrument: {}".format(instrument))

        if trading_symbol is not None:
            break

    # debugging line that forces the trade to not be made
    print("[?] Trading: ", trading is True)
    trading = False
    if trading is True:
        # decide how much to buy # TODO
        quant = 10

        # then submit a buy order
        # broker.submit_order(
        #     api_reference=alpaca_api,
        #     ticker=trading_symbol,
        #     qty=quant,
        #     transaction_side="buy",
        #     ttype="market",
        #     time_in_force="ioc"
        # )
