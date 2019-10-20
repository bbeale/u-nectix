#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import time_formatter, set_candlestick_df
from requests.exceptions import HTTPError
from finta import TA
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
            self.dataframe[ticker] = self.get_macd_mfi_stoch(ticker)
        return self.dataframe

    def g3t_m0ar_indicat0rszz(self):
        """Loop through tickers and append indicators to that ticker's dataframe"""
        for ticker in self.dataframe.keys():
            self.dataframe[ticker] = self.get_vzo_dmi_apz(ticker)
        return self.dataframe

    def get_cluster(self):
        """Loop through tickers and append indicators to that ticker's dataframe"""
        for ticker in self.dataframe.keys():
            self.dataframe[ticker] = self.cluster_prep(ticker)
        return self.dataframe

    def get_bars(self, ticker, backdate=None):
        """Get bars for a ticker symbol

        :param ticker: a stock ticker symbol
        :param backdate: start of the historic data lookup period. If none, defaults to the last 13 weeks (1 quarter)
        :return: dataframe built from barset objects, including indicators
        """
        if not ticker or ticker is None:
            raise ValueError("Invalid ticker value")

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))
        bars = None
        try:
            bars = self.api.get_barset(ticker, "1D", after=backdate)[ticker]
        except HTTPError:
            print("Retrying...")
            time.sleep(3)
            try:
                bars = self.api.get_barset(ticker, "1D", after=backdate)[ticker]
            except HTTPError:
                raise HTTPError
        finally:
            return bars

    def get_macd_mfi_stoch(self, ticker, backdate=None):
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

        bars = self.get_bars(ticker, backdate)
        data = set_candlestick_df(bars)

        print(data["close"].iloc[-1], data["close"].iloc[-2], data["close"].iloc[-3])

        # get MACD
        macd = TA.MACD(data)
        _macds = macd["MACD"]
        _signals = macd["SIGNAL"]

        # get money flow index
        mfi = TA.MFI(data)

        # get stochastic oscillator
        stoch = TA.STOCH(data)

        data["ticker"]  = ticker
        data["macd"]    = _macds
        data["signal"]  = _signals
        data["mfi"]     = mfi
        data["stoch"]   = stoch

        return data

    def get_vzo_dmi_apz(self, ticker, backdate=None):
        """Given a ticker symbol and a historic, calculate various indicators from then to now.

        Currently, VZO, DMI and APZ oscillator are implemented.

        :param ticker: a stock ticker symbol
        :param backdate: start of the historic data lookup period. If none, defaults to the last 13 weeks (1 quarter)
        :return: dataframe built from barset objects, including indicators
        """
        if not ticker or ticker is None:
            raise ValueError("Invalid ticker value")

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        bars = self.get_bars(ticker, backdate)
        data = set_candlestick_df(bars)

        print(data["close"].iloc[-1], data["close"].iloc[-2], data["close"].iloc[-3])

        # get VZO   - bullish trend range 5-40%; oversold - -40%; extremely oversold -60%
        vzo = TA.VZO(data)

        # get DMI   - buy sign when + line crosses over - line
        dmi = TA.DMI(data)

        # get APZ   - volatility indicator
        apz = TA.APZ(data)

        data["ticker"]  = ticker
        data["vzo"]     = vzo
        data["dmi_p"]   = dmi["DI+"]
        data["dmi_m"]   = dmi["DI-"]
        data["apz_u"]   = apz["UPPER"]
        data["apz_l"]   = apz["LOWER"]

        return data

    def compare_macd_vmacd(self, ticker, backdate=None):
        """Compare different MACD indicators."""
        if not ticker or ticker is None:
            raise ValueError("Invalid ticker value")

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        bars = self.get_bars(ticker, backdate)
        data = set_candlestick_df(bars)

        # get MACD
        macd        = TA.MACD(data)
        _macds      = macd["MACD"]
        _signals    = macd["SIGNAL"]

        # get VW_MACD
        vwmacd      = TA.VW_MACD(data)
        _vmacds      = vwmacd["MACD"]
        _vsignals    = vwmacd["SIGNAL"]

        data["ticker"]  = ticker
        data["macd"]    = _macds
        data["signal"]  = _signals
        data["vwmacd"]    = _vmacds
        data["vwsignal"]  = _vsignals

        return data

    def cluster_prep(self, ticker, backdate=None):
        """Compare different MACD indicators."""
        if not ticker or ticker is None:
            raise ValueError("Invalid ticker value")

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        bars = self.get_bars(ticker, backdate)
        data = set_candlestick_df(bars)

        # get Bollinger bands
        bbands = TA.BBANDS(data)
        _bb_up = bbands["BB_UPPER"]
        _bb_mid = bbands["BB_MIDDLE"]
        _bb_low = bbands["BB_LOWER"]

        # get MACD
        macd = TA.MACD(data)
        _macds = macd["MACD"]
        _signals = macd["SIGNAL"]

        # get VW_MACD
        vwmacd      = TA.VW_MACD(data)
        _vmacds      = vwmacd["MACD"]
        _vsignals    = vwmacd["SIGNAL"]

        # get money flow index
        mfi = TA.MFI(data)

        # get stochastic oscillator
        stoch = TA.STOCH(data)

        # get VZO   - bullish trend range 5-40%; oversold - -40%; extremely oversold -60%
        vzo = TA.VZO(data)

        # get APZ   - volatility indicator -- might be useful in sentiment comparison
        apz = TA.APZ(data)

        # get DMI   - buy sign when + line crosses over - line
        dmi = TA.DMI(data)
        # ¯\_(ツ)_/¯ seems to be a bug in finta DMI implementation - returning lists of NaN
        # TODO: investigate - https://github.com/bbeale/finta
        # Seems to be appending the values I am expecting it to return directly to my dataframe instead of returning them.
        # Hmm...
        # data["dmi_p"]       = dmi["DMp"]
        # data["dmi_m"]       = dmi["DMm"]

        data["ticker"]          = ticker
        data["bb_up"]           = _bb_up
        data["bb_mid"]          = _bb_mid
        data["bb_low"]          = _bb_low
        data["macd"]            = _macds
        data["signal"]          = _signals
        data["vwmacd"]          = _vmacds
        data["vwsignal"]        = _vsignals
        data["mfi"]             = mfi
        data["stoch"]           = stoch
        data["vzo"]             = vzo
        data["apz_u"]           = apz["UPPER"]
        data["apz_l"]           = apz["LOWER"]
        # Percent changes
        data["bb_up_ptc"]       = _bb_up.pct_change()
        data["bb_mid_ptc"]      = _bb_mid.pct_change()
        data["bb_low_ptc"]      = _bb_low.pct_change()
        data["macd_ptc"]        = _macds.pct_change()
        data["signal_ptc"]      = _signals.pct_change()
        data["vwmacd_ptc"]      = _vmacds.pct_change()
        data["vwsignal_ptc"]    = _vsignals.pct_change()
        data["mfi_ptc"]         = mfi.pct_change()
        data["stoch_ptc"]       = stoch.pct_change()
        data["vzo_ptc"]         = vzo.pct_change()
        data["apz_u_ptc"]       = apz["UPPER"].pct_change()
        data["apz_l_ptc"]       = apz["LOWER"].pct_change()

        return data
