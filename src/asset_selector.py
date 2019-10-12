#!/usr/bin/env python
# -*- coding: utf-8 -*-
from alpaca_functions import bullish_candlestick_patterns, time_formatter
import pandas as pd
import time
import sys


class AssetSelector:

    def __init__(self, alpaca_api_interface):

        if not alpaca_api_interface or alpaca_api_interface is None:
            raise ValueError("Alpaca API interface instance required")

        self.api            = alpaca_api_interface
        self.account        = self.api.get_account()
        self.buying_power   = self.account.buying_power

    def get_stuff_to_trade_v2(self, backdate=None):

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        # Check if our account is restricted from trading.
        if self.account.trading_blocked:
            print("Account is currently restricted from trading.")
            sys.exit(-1)

        # Check how much money we can use to open new positions.
        print("${} is available as buying power.".format(self.buying_power))

        active_assets = self.api.list_assets(status="active")

        # Filter the assets down to just those on NASDAQ.
        assets = [a for a in active_assets if a.tradable and a.shortable and a.marginable and a.easy_to_borrow]
        bullish_to_compare = {}
        bearish_to_compare = {}
        for i in assets:

            symbol          = i.symbol
            start           = backdate
            barset          = self.api.get_barset(symbol, "1D", after=start)
            symbol_bars     = barset[symbol]

            df              = pd.DataFrame()
            df["time"]      = [bar.t for bar in symbol_bars if bar is not None]
            df["open"]      = [bar.o for bar in symbol_bars if bar is not None]
            df["high"]      = [bar.h for bar in symbol_bars if bar is not None]
            df["low"]       = [bar.l for bar in symbol_bars if bar is not None]
            df["close"]     = [bar.c for bar in symbol_bars if bar is not None]
            df["volume"]    = [bar.v for bar in symbol_bars if bar is not None]

            pattern         = bullish_candlestick_patterns(df.iloc[-3], df.iloc[-2], df.iloc[-1])

            if pattern is None:
                continue

            if pattern in ["hammer", "inverseHammer"]:
                bullish_to_compare[symbol] = df

            if pattern in ["bullishEngulfing", "piercingLine", "morningStar", "threeWhiteSoldiers"]:
                bearish_to_compare[symbol] = df

            if len(bearish_to_compare) is 5 or len(bullish_to_compare) is 5:
                if len(bearish_to_compare) > len(bullish_to_compare):
                    return bearish_to_compare
                elif len(bullish_to_compare) > len(bearish_to_compare):
                    return bullish_to_compare

