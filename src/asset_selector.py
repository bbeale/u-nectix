#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import bullish_candlestick_patterns, time_formatter, num_bars
from src.edgar_interface import EdgarInterface
from requests.exceptions import HTTPError
import pandas as pd
import inspect
import json
import time


class AssetSelector:

    def __init__(self, alpaca_api_interface, backdate=None, edgar_token=None):

        if not alpaca_api_interface or alpaca_api_interface is None:
            raise ValueError("Alpaca API interface instance required.")

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        self.api                = alpaca_api_interface
        self.backdate           = backdate
        self.edgar_token        = None

        if edgar_token is not None:
            self.edgar_token = edgar_token
            self.ei = EdgarInterface(self.edgar_token)

        self.raw_assets         = None
        self.tradeable_assets   = None
        self.bulls              = dict()
        self.bears              = dict()
        self.recent_filings     = dict()
        self.assets_by_filing   = dict()

        self.populate()

    def populate(self):

        self.get_assets()
        self.extract_tradeable_assets(self.raw_assets)

    def get_assets(self):
        """Get assets from Alpaca API.

        :return:
        """
        result = None
        try:
            result = self.api.list_assets(status="active")
        except HTTPError as httpe:
            print(httpe, "- Unable to get assets. Retrying in 3s...")
            time.sleep(3)
            try:
                result = self.api.list_assets(status="active")
            except HTTPError as httpe:
                print(httpe, "- Unable to get assets.")
                raise httpe
        finally:
            self.raw_assets = result

    def extract_tradeable_assets(self, asset_list):
        """Extract tradeable assets from API results.

        :param asset_list:
        :return:
        """
        if not asset_list or asset_list is None or len(asset_list) is 0:
            raise ValueError
        self.tradeable_assets = [a for a in asset_list if a.tradable and a.shortable and a.marginable and a.easy_to_borrow]

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
            print(httpe, "- Unable to get barset for {}. Retrying in 3s...".format(symbol))
            time.sleep(3)
            try:
                result = self.api.get_barset(symbol, period, after=starting_time)
            except HTTPError as httpe:
                print(httpe, "- Unable to get barset or barset is None.")
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
            raise ValueError("Bar object cannot be None.")

        if not symbol or symbol is None:
            raise ValueError("Must give a valid ticker symbol.")

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
            raise ValueError("Dataframe cannot be None.")

        pattern = bullish_candlestick_patterns(dataframe.iloc[-3], dataframe.iloc[-2], dataframe.iloc[-1])
        candle = None

        if pattern in ["hammer", "inverseHammer"]:
            candle = "bull"

        if pattern in ["bullishEngulfing", "piercingLine", "morningStar", "threeWhiteSoldiers"]:
            candle = "bear"

        return candle

    def evaluate_candlesticks(self, asset_list, fname, barcount, poolsize=5):
        """Given a list of assets, evaluate which ones are bullish or bearish and return a sample of each.

        :param asset_list:
        :param fname:
        :param barcount:
        :param poolsize:
        :return:
        """
        if not asset_list or asset_list is None:
            raise ValueError("Asset list cannot be None.")

        if not fname or fname is None:
            raise ValueError("Name of calling entity required.")

        if not barcount or barcount is None:
            barcount = 64

        if not poolsize or poolsize is None or poolsize is 0:
            poolsize = 5

        calling_fn = fname
        results = dict()

        for i in asset_list:
            if len(results.keys()) == poolsize:
                print(results.keys())
                return

            try:
                df, eval_result = self.evaluate_candlestick(i, barcount)
            except DataframeException:
                continue
            except CandlestickException:
                continue
            else:
                if eval_result in calling_fn and len(results.keys()) < poolsize:
                    results[i.symbol] = df

                    print("Ticker: {}\nPoolsize: {}\nResult Length: {}".format(
                        i.symbol, poolsize, len(results.keys())))

    def evaluate_candlestick(self, asset, barcount):
        """Return the candlestick pattern and dataframe of an asset if a bullish or bearish pattern is detected among the last three closing prices.

            Bullish patterns: hammer, inverseHammer
            Bearish patterns: bullishEngulfing, piercingLine, morningStar, threeWhiteSoldiers

        :param asset:
        :param barcount:
        :return:
        """
        if not asset or asset is None:
            raise ValueError("Unable to evaluate a None asset.")

        barset = self.get_barset(asset.symbol, "1D", self.backdate)
        if barset is None:
            raise DataframeException("Invalid barset -- cannot be None.")

        if num_bars(barset[asset.symbol], barcount) is False:
            raise DataframeException("Insufficient data.")

        df = self.extract_bar_data(barset, asset.symbol)

        # evaluate candlestick direction
        candle_pattern = self.candle_pattern_direction(df)
        if candle_pattern is not None:
            return df, candle_pattern
        else:
            raise CandlestickException("Pattern not detected.")

    def bullish_candlesticks(self, barcount=64, poolsize=5):
        """Return assets with a bullish pattern of closing prices over a given period.

        :param barcount:
        :param poolsize:
        :return:
        """
        self.evaluate_candlesticks(self.tradeable_assets, fname=inspect.stack()[0][3], barcount=barcount, poolsize=poolsize)

        # return bulls
        return self.bulls

    def bearish_candlesticks(self, barcount=64, poolsize=5):
        """Return assets with a bearish pattern of closing prices over a given period.

        :param barcount:
        :param poolsize:
        :return:
        """
        self.evaluate_candlesticks(self.tradeable_assets, fname=inspect.stack()[0][3], barcount=barcount, poolsize=poolsize)

        # return bears
        return self.bears

    def sec_filings(self, barcount=64, poolsize=5, form_type="8-K", backdate=None):
        """Return tradeable asets with recent SEC filings.

        :param barcount:
        :param poolsize:
        :param form_type:
        :param backdate:
        :return:
        """
        if not self.edgar_token or self.edgar_token is None:
            raise NotImplementedError

        if not backdate or backdate is None:
            # backdate = time_formatter(time.time() - 604800, time_format="%Y-%m-%d")
            # using a longer window only for debugging purposes -- just to make sure I have results quickly
            backdate = time_formatter(time.time() - (604800 * 26), time_format="%Y-%m-%d")

        date            = time_formatter(time.time(), time_format="%Y-%m-%d")

        # Filter the assets down to just those on NASDAQ.
        active_assets   = self.get_assets()
        assets          = self.extract_tradeable_assets(active_assets)

        print("Going through assets looking for firms with recent SEC filings")
        for i in assets:

            self.get_filings(i, backdate=backdate, date=date, form_type=form_type)

            if len(self.recent_filings.keys()) >= poolsize:
                break
            else:
                continue

        self.tradeable_assets_by_filings(barcount)

        return self.assets_by_filing

    def get_filings(self, asset, backdate, date, form_type="8-K"):
        """Given a trading entity, get SEC filings in the date range.

        :param asset:
        :param backdate:
        :param date:
        :param form_type:
        :return:
        """
        filings = self.ei.get_sec_filings(asset.symbol, backdate, date, form_type=form_type)

        # If none are found, lengthen the lookback window a couple times
        if filings["total"] is 0:
            print("No recent filings found for {}. Looking back 2 weeks".format(asset.symbol))
            backdate = time_formatter(time.time() - (604800 * 2), time_format="%Y-%m-%d")
            filings = self.ei.get_sec_filings(asset.symbol, backdate, date, form_type=form_type)

        if filings["total"] is 0:
            print("No filings found. Looking back 4 weeks")
            backdate = time_formatter(time.time() - (604800 * 4), time_format="%Y-%m-%d")
            filings = self.ei.get_sec_filings(asset.symbol, backdate, date, form_type=form_type)

        if filings["total"] > 0:
            print("\tAdded:", asset.symbol, " symbols:", len(self.recent_filings.keys()) + 1)
            filings = json.dumps(filings)
            self.recent_filings[asset.symbol] = filings

    def tradeable_assets_by_filings(self, barcount=64):
        """Populate tradeable assets based on discovered SEC filings.

        :return:
        """
        for i in self.recent_filings.keys():
            # I think I need my original 13 week window here for consistency with get_assets_by_candlestick_pattern
            backdate    = time_formatter(time.time() - (604800 * 13))

            barset      = self.get_barset(i.symbol, "1D", backdate)

            if num_bars(barset[i.symbol], barcount) is False:
                continue

            df = self.extract_bar_data(barset, i.symbol)
            self.assets_by_filing[i.symbol] = df


class AssetException(Exception):
    pass


class CandlestickException(AssetException):
    pass


class DataframeException(AssetException):
    pass
