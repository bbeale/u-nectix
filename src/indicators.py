#!/usr/bin/env python
# -*- coding: utf-8 -*-
from alpaca_functions import time_formatter
from finta import TA
import pandas as pd
import time


class Indicators:

    def __init__(self, alpaca_api_interface, dataframe):

        if not alpaca_api_interface or alpaca_api_interface is None:
            raise ValueError("Alpaca API interface instance required")
        self.api            = alpaca_api_interface
        self.account        = self.api.get_account()
        self.buying_power   = self.account.buying_power
        self.dataframe      = dataframe

    def get_indicators(self):
        """Loop through tickers and append indicators to that ticker's dataframe"""
        for ticker in self.dataframe.keys():
            self.dataframe[ticker] = self.calculate_indicators_v2(ticker)
        return self.dataframe

    def calculate_indicators_v2(self, ticker, backdate=None):
        """Given a ticker symbol and a historic, calculate various indicators from then to now.

        Currently, MACD, MFI and stochastic oscillators are implemented.

        :param ticker: a stock ticker symbol
        :param backdate: start of the historic data lookup period. If none, defaults to the last 13 weeks (1 quarter)
        :return: dataframe built from barset objects, including indicators
        """
        if not ticker or ticker is None:
            raise ValueError("Invalid ticker value")

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        try:
            bars = self.api.get_barset(ticker, "1D", after=backdate)[ticker]
        except OSError:
            raise OSError

        data = pd.DataFrame()
        data["time"] = [bar.t for bar in bars if bar is not None]
        data["open"] = [bar.o for bar in bars if bar is not None]
        data["high"] = [bar.h for bar in bars if bar is not None]
        data["low"] = [bar.l for bar in bars if bar is not None]
        data["close"] = [bar.c for bar in bars if bar is not None]
        data["volume"] = [bar.v for bar in bars if bar is not None]

        print(data["close"].iloc[-1], data["close"].iloc[-2], data["close"].iloc[-3])

        # get MACD
        macd = TA.MACD(data)
        _macds = macd["MACD"]
        _signals = macd["SIGNAL"]

        # get money flow index
        mfi = TA.MFI(data)

        # get stochastic oscillator
        stoch = TA.STOCH(data)

        data["ticker"] = ticker
        data["macd"] = _macds
        data["signal"] = _signals
        data["mfi"] = mfi
        data["stoch"] = stoch

        return data
