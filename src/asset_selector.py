#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import bullish_candlestick_patterns, time_formatter, num_bars
from src.edgar_interface import EdgarInterface
from requests.exceptions import HTTPError
import pandas as pd
import json
import time


class AssetSelector:

    def __init__(self, alpaca_api_interface, edgar_token=None):

        if not alpaca_api_interface or alpaca_api_interface is None:
            raise ValueError("Alpaca API interface instance required")

        self.api            = alpaca_api_interface
        self.edgar_token    = None

        if edgar_token is not None:
            self.edgar_token = edgar_token

    def get_assets(self):
        """Get assets from Alpaca API.

        :return:
        """
        result = None
        try:
            result = self.api.list_assets(status="active")
        except HTTPError as httpe:
            print(httpe, "- Unable to get assets. Retrying...")
            time.sleep(3)
            try:
                result = self.api.list_assets(status="active")
            except HTTPError as httpe:
                print(httpe, "- Unable to get assets.")
                raise httpe
        finally:
            return result

    @classmethod
    def extract_tradeable_assets(cls, asset_list):
        """Extract tradeable assets from API results.

        :param asset_list:
        :return:
        """
        if not asset_list or asset_list is None or len(asset_list) is 0:
            raise ValueError
        return [a for a in asset_list if a.tradable and a.shortable and a.marginable and a.easy_to_borrow]

    def get_barset(self, symbol, period, starting_time):
        """Get a set of bars from the API given a symbol, a time period and a starting time.

        :param symbol:
        :param period:
        :param starting_time:
        :return:
        """
        result = None
        try:
            result = self.api.get_barset(symbol, period, after=starting_time)
        except HTTPError as httpe:
            print(httpe, "- Unable to get barset. Retrying...")
            time.sleep(3)
            try:
                result = self.api.get_barset(symbol, period, after=starting_time)
            except HTTPError as httpe:
                print(httpe, "- Unable to get barset.")
                raise httpe
        finally:
            return result

    @classmethod
    def extract_bar_data(cls, bar_object, symbol):
        """Given a bar object from the Alpaca API, return a stripped down dataframe in ohlcv format.

        :param bar_object:
        :param symbol:
        :return:
        """
        if not bar_object or bar_object is None:
            raise ValueError

        if not symbol or symbol is None:
            raise ValueError

        bars = bar_object[symbol]
        df = pd.DataFrame()

        try:
            df["time"]      = [bar.t for bar in bars if bar is not None]
            df["open"]      = [bar.o for bar in bars if bar is not None]
            df["high"]      = [bar.h for bar in bars if bar is not None]
            df["low"]       = [bar.l for bar in bars if bar is not None]
            df["close"]     = [bar.c for bar in bars if bar is not None]
            df["volume"]    = [bar.v for bar in bars if bar is not None]
        except ValueError:
            raise ValueError
        finally:
            return df

    @classmethod
    def candle_pattern_direction(cls, dataframe):
        """Given a series, get the candlestick pattern of the last 3 periods.

        :param dataframe:
        :return:
        """
        if dataframe is None:
            raise ValueError

        pattern = bullish_candlestick_patterns(dataframe.iloc[-3], dataframe.iloc[-2], dataframe.iloc[-1])
        candle = None

        if pattern in ["hammer", "inverseHammer"]:
            candle = "bull"

        if pattern in ["bullishEngulfing", "piercingLine", "morningStar", "threeWhiteSoldiers"]:
            candle = "bear"

        return candle

    def evaluate_assets(self, asset_list, backdate, poolsize=5):
        """Given a list of assets, evaluate which ones are bullish or bearish and return a sample of each.

        :param asset_list:
        :param backdate:
        :param poolsize:
        :return:
        """
        if not asset_list or asset_list is None:
            raise ValueError

        if not backdate or backdate is None:
            raise ValueError

        if not poolsize or poolsize is None or poolsize is 0:
            poolsize = 5

        _bulls = dict()
        _bears = dict()

        for i in asset_list:
            symbol  = i.symbol
            print("ticker:", symbol)
            start   = backdate
            barset  = self.get_barset(symbol, "1D", start)

            if num_bars(barset[symbol], 63) is False:
                continue

            df = self.extract_bar_data(barset, symbol)

            # evaluate candlestick direction
            candle_pattern = self.candle_pattern_direction(df)

            if candle_pattern is "bull" and len(_bulls) < poolsize:
                _bulls[symbol] = df

            if candle_pattern is "bear" and len(_bears) < poolsize:
                _bears[symbol] = df

            if len(_bulls.keys()) == poolsize and len(_bears.keys()) == poolsize:
                return _bulls, _bears

    def get_assets_bullish_candlestick(self, backdate=None):

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        # get active, tradeable assets
        active_assets   = self.get_assets()
        assets          = self.extract_tradeable_assets(active_assets)
        bulls           = self.evaluate_assets(assets, backdate)[0]

        return bulls

    def get_assets_bearish_candlestick(self, backdate=None):

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        # get active, tradeable assets
        active_assets   = self.get_assets()
        assets          = self.extract_tradeable_assets(active_assets)
        bears           = self.evaluate_assets(assets, backdate)[1]

        return bears

    def get_assets_with_8k_filings(self, backdate=None):

        if not self.edgar_token or self.edgar_token is None:
            raise NotImplementedError

        if not backdate or backdate is None:
            # backdate = time_formatter(time.time() - 604800, time_format="%Y-%m-%d")
            # using a longer window only for debugging purposes -- just to make sure I have results quickly
            backdate = time_formatter(time.time() - (604800 * 26), time_format="%Y-%m-%d")

        date    = time_formatter(time.time(), time_format="%Y-%m-%d")
        ei      = EdgarInterface(self.edgar_token)

        # Filter the assets down to just those on NASDAQ.
        active_assets   = self.get_assets()
        assets          = self.extract_tradeable_assets(active_assets)
        recent_filings  = dict()

        print("Going through assets looking for firms with recent SEC filings")
        for i in assets:

            symbol      = i.symbol
            start       = backdate
            filings     = ei.get_sec_filings(symbol, start, date, form_type="8-K")

            # If none are found, lengthen the lookback window a couple times
            if filings["total"] is 0:
                print("No recent filings found for {}. Looking back 2 weeks".format(symbol))
                start = time_formatter(time.time() - (604800 * 2), time_format="%Y-%m-%d")
                filings = ei.get_sec_filings(symbol, start, date, form_type="8-K")

            if filings["total"] is 0:
                print("No filings found. Looking back 4 weeks")
                start = time_formatter(time.time() - (604800 * 4), time_format="%Y-%m-%d")
                filings = ei.get_sec_filings(symbol, start, date, form_type="8-K")

            if filings["total"] > 0:
                print("\tAdded:", i.symbol, " symbols:", len(recent_filings.keys()) + 1)
                filings = json.dumps(filings)
                recent_filings[symbol] = filings

            if len(recent_filings.keys()) >= 5:
                break
            else:
                continue

        assets_to_trade = dict()

        for i in recent_filings.keys():
            # I think I need my original 13 week window here for consistency with get_assets_by_candlestick_pattern
            backdate    = time_formatter(time.time() - (604800 * 13))
            symbol      = i.symbol
            start       = backdate
            barset      = self.get_barset(symbol, "1D", start)

            if num_bars(barset[symbol], 64) is False:
                continue

            df = self.extract_bar_data(barset, symbol)
            assets_to_trade[symbol] = df
        return assets_to_trade
