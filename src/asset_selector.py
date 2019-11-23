#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import bullish_candlestick_patterns, time_formatter, num_bars, set_candlestick_df
from src.indicators import Indicators
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

        try:
            df = set_candlestick_df(bars)
        except ValueError:
            raise ValueError
        else:
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
        direction = None

        if pattern in ["hammer", "inverseHammer"]:
            direction = "bull"

        if pattern in ["bullishEngulfing", "piercingLine", "morningStar", "threeWhiteSoldiers"]:
            direction = "bear"

        return direction, pattern

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
        print("Ticker".ljust(10), "Last".ljust(10), "Change".ljust(10), "% Change".ljust(10), "MACD Buy?".ljust(10), "MFI".ljust(10), "VZO".ljust(10), "Stochastic Oscillator".ljust(10), "Pattern")
        print("{:<30}".format("–" * 45))

        for i in asset_list:
            if len(results.keys()) == poolsize:
                return results

            try:
                df, eval_result, pattern = self.evaluate_candlestick(i, barcount)
            except DataframeException:
                continue
            except CandlestickException:
                continue
            else:
                if eval_result in calling_fn and len(results.keys()) < poolsize:

                    results[i.symbol] = df
                    _macd = Indicators.get_macd(df)
                    mfi = Indicators.get_mfi(df)
                    vzo = Indicators.get_vzo(df)
                    stoch = Indicators.get_stoch(df)
                    macd = _macd["MACD"]
                    signal = _macd["SIGNAL"]

                    num_criteria = 0

                    # TODO: factor these buy signals out into methods
                    # calculate macd buy signal
                    # signal is true when macd bullish crossover of signal and mmacd < 0
                    try:
                        macd_buysignal = macd.iloc[-1] < 0 and min(macd.iloc[-4:-2]) < signal.iloc[-1] and macd.iloc[-1] > \
                                         signal.iloc[-1]
                    except IndexError:
                        # Throwing away due to index errors, will handle later
                        continue

                    # calculate mfi buy signal via bullish 10% crossover
                    try:
                        mfi_buysignal = vzo.iloc[-1] > -40 and min(vzo.iloc[-4:-2]) <= -40
                    except IndexError:
                        continue
                    else:
                        if mfi_buysignal:
                            num_criteria += 1

                    # calculate the VZO buy signal -- look for bullish -40% crossover
                    try:
                        vzo_buysignal = mfi.iloc[-1] > 10 and min(mfi.iloc[-4:-2]) <= 10
                    except IndexError:
                        continue
                    else:
                        if vzo_buysignal:
                            num_criteria += 1

                    # calculate stochastic buy signal via bullish 10% crossover
                    try:
                        stoch_buysignal = stoch.iloc[-1] > 10 and min(stoch.iloc[-4:-2]) <= 10
                    except IndexError:
                        continue
                    else:
                        if stoch_buysignal:
                            num_criteria += 1

                    if macd_buysignal and num_criteria >= 1:
                        # display the result if it meets criteria

                        # TODO: make this actually return or append asset selection again

                        print(i.symbol.ljust(10), "${:.2f}".format(df["close"].iloc[-1]).ljust(10), "${:.2f}".format(df["close"].iloc[-1] - df["close"].iloc[-2]).ljust(10), "{:.2f}%".format(df["close"].pct_change().iloc[-1] - df["close"].pct_change().iloc[-2]).ljust(10), str(macd_buysignal).ljust(10), str(mfi_buysignal).ljust(10), str(vzo_buysignal).ljust(10), str(stoch_buysignal).ljust(10), str(pattern))
        print("done")

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
        candle, pattern = self.candle_pattern_direction(df)
        if candle is not None:
            return df, candle, pattern
        else:
            raise CandlestickException("Pattern not detected.")

    def bullish_candlesticks(self, barcount=64, poolsize=5):
        """Return assets with a bullish pattern of closing prices over a given period.

        :param barcount:
        :param poolsize:
        :return:
        """
        self.bulls = self.evaluate_candlesticks(self.tradeable_assets, fname=inspect.stack()[0][3], barcount=barcount, poolsize=poolsize)

        # return bulls
        return self.bulls

    def bearish_candlesticks(self, barcount=64, poolsize=5):
        """Return assets with a bearish pattern of closing prices over a given period.

        :param barcount:
        :param poolsize:
        :return:
        """
        self.bears = self.evaluate_candlesticks(self.tradeable_assets, fname=inspect.stack()[0][3], barcount=barcount, poolsize=poolsize)

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
