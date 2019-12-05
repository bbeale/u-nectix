#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import bullish_candlestick_patterns, time_formatter, num_bars, set_candlestick_df
from src.trade_signal import TradeSignal as TS, TradeSignalException as TSError
from src.finta_interface import Indicator as indicators
from src.edgar_interface import EdgarInterface
from requests.exceptions import HTTPError
import inspect
import json
import time

class AssetException(Exception):
    pass

class CandlestickException(AssetException):
    pass

class DataframeException(AssetException):
    pass

class AssetSelector:

    @classmethod
    def extract_bar_data(cls, bar_object, symbol):
        """Given a bar object from the Alpaca API, return a stripped down dataframe in ohlcv format.

        :param bar_object:
        :param symbol:
        :return:
        """
        if not bar_object or bar_object is None:
            raise ValueError("[!] Bar object cannot be None.")

        if not symbol or symbol is None:
            raise ValueError("[!] Must give a valid ticker symbol.")

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
            raise ValueError("[!] Dataframe cannot be None.")

        pattern = bullish_candlestick_patterns(dataframe.iloc[-3], dataframe.iloc[-2], dataframe.iloc[-1])
        direction = None

        if pattern in ["hammer", "inverseHammer"]:
            direction = "bull"

        if pattern in ["bullishEngulfing", "piercingLine", "morningStar", "threeWhiteSoldiers"]:
            direction = "bear"

        return direction, pattern

    def __init__(self, alpaca_api_interface, backdate=None, edgar_token=None):

        if not alpaca_api_interface or alpaca_api_interface is None:
            raise ValueError("[!] Alpaca API interface instance required.")

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
        self.top_gainers        = dict()
        self.top_losers         = dict()

        self.populate()

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

    def _filter_bullish_assets(self, asset_list, fname, barcount, poolsize=5):
        """Given a list of assets, evaluate which ones are bullish and return a sample of each.

        :param asset_list:
        :param fname:
        :param barcount:
        :param poolsize:
        :return:
        """
        if not asset_list or asset_list is None:
            raise ValueError("[!] Asset list cannot be None.")

        if not fname or fname is None:
            raise ValueError("[!] Name of calling entity required.")

        # if not barcount or barcount is None:
        #     barcount = 64

        if not poolsize or poolsize is None or poolsize is 0:
            poolsize = 5

        calling_fn = fname
        results = dict()
        print("Bulls".center(45))
        print()
        print("Ticker".ljust(10), "Last".ljust(10), "Change".ljust(10), "% Change".ljust(10), "MACD?".ljust(10), "MFI?".ljust(10), "VZO?".ljust(10), "Stoch?".ljust(10), "Pattern")
        print("{:<30}".format("–" * 70))

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

                    num_criteria = 0
                    try:
                        macd_signal = TS.macd_buy(df)
                        mfi_signal = TS.mfi_buy(df)
                        vzo_signal = TS.vzo_buy(df)
                        stoch_signal = TS.stoch_buy(df)
                    except TSError:
                        raise TSError("[!] Failed to compute one or more expected buy signals.")

                    if mfi_signal:
                        num_criteria += 1

                    if vzo_signal:
                        num_criteria += 1

                    if stoch_signal:
                        num_criteria += 1

                    if macd_signal and num_criteria >= 1:
                        # display the result if it meets criteria
                        results[i.symbol] = df
                        print(i.symbol.ljust(10), "${:.2f}".format(df["close"].iloc[-1]).ljust(10), "${:.2f}".format(df["close"].iloc[-1] - df["close"].iloc[-2]).ljust(10), "{:.2f}%".format(df["close"].pct_change().iloc[-1] - df["close"].pct_change().iloc[-2]).ljust(10), str(macd_signal).ljust(10), str(mfi_signal).ljust(10), str(vzo_signal).ljust(10), str(stoch_signal).ljust(10), str(pattern))

    def _filter_bearish_assets(self, asset_list, fname, barcount, poolsize=5):
        """Given a list of assets, evaluate which ones are bearish and return a sample of each.

        :param asset_list:
        :param fname:
        :param barcount:
        :param poolsize:
        :return:
        """
        if not asset_list or asset_list is None:
            raise ValueError("[!] Asset list cannot be None.")

        if not fname or fname is None:
            raise ValueError("[!] Name of calling entity required.")

        if not barcount or barcount is None:
            barcount = 64

        if not poolsize or poolsize is None or poolsize is 0:
            poolsize = 5

        calling_fn = fname
        results = dict()
        print("Bears".center(45))
        print()
        print("Ticker".ljust(10), "Last".ljust(10), "Change".ljust(10), "% Change".ljust(10), "MACD?".ljust(10), "MFI?".ljust(10), "VZO?".ljust(10), "Stoch?".ljust(10), "Pattern")
        print("{:<30}".format("–" * 70))

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

                    num_criteria = 0
                    try:
                        macd_signal = TS.macd_sell(df)
                        mfi_signal = TS.mfi_sell(df)
                        vzo_signal = TS.vzo_sell(df)
                        stoch_signal = TS.stoch_sell(df)
                    except TSError:
                        raise TSError("[!] Failed to compute one or more expected sell signals.")

                    if mfi_signal:
                        num_criteria += 1

                    if vzo_signal:
                        num_criteria += 1

                    if stoch_signal:
                        num_criteria += 1

                    if macd_signal and num_criteria >= 1:
                        # display the result if it meets criteria
                        results[i.symbol] = df
                        print(i.symbol.ljust(10), "${:.2f}".format(df["close"].iloc[-1]).ljust(10), "${:.2f}".format(df["close"].iloc[-1] - df["close"].iloc[-2]).ljust(10), "{:.2f}%".format(df["close"].pct_change().iloc[-1] - df["close"].pct_change().iloc[-2]).ljust(10), str(macd_signal).ljust(10), str(mfi_signal).ljust(10), str(vzo_signal).ljust(10), str(stoch_signal).ljust(10), str(pattern))

    def _filter_top_gainers(self):
        """Use Polygon endpoint to get a list of top 20 "gainers".

            :return:
            """
        print("Gainers".center(45))
        print()
        print("Ticker".ljust(10), "Last".ljust(10), "Change".ljust(10), "% Change".ljust(10), "MACD Buy?".ljust(10),
            "MFI".ljust(10), "VZO".ljust(10), "Stochastic")
        print("{:<30}".format("–" * 70))

        gainers = self.api.polygon.gainers_losers()

        res = []
        for symbol in range(len(gainers)):

            ticker = gainers[symbol].ticker
            bars = self.api.get_barset(ticker, "1D", after=self.backdate)
            dataframe = self.extract_bar_data(bars, ticker)

            # buy signals
            try:
                macd_signal = TS.macd_buy(dataframe)
                mfi_signal = TS.mfi_buy(dataframe)
                vzo_signal = TS.vzo_buy(dataframe)
                stoch_signal = TS.stoch_buy(dataframe)
            except TSError:
                raise TSError("[!] Failed to compute one or more expected buy signals.")

            print(self.api.polygon.gainers_losers()[symbol].ticker.ljust(10),
                "${:.2f}".format(self.api.polygon.gainers_losers()[symbol].lastTrade["p"]).ljust(10),
                "${:.2f}".format(self.api.polygon.gainers_losers()[symbol].todaysChange).ljust(10),
                "{:.2f}%".format(self.api.polygon.gainers_losers()[symbol].todaysChangePerc).ljust(10),
                str(macd_signal).ljust(10),
                str(mfi_signal).ljust(10),
                str(vzo_signal).ljust(10),
                str(stoch_signal).ljust(10)
            )
            res.append(self.api.polygon.gainers_losers()[symbol])
        return res

    def _filter_top_losers(self):
        """Use Polygon endpoint to get a list of top 20 "losers".

        :return:
        """
        print("Losers".center(45))
        print()
        print("Ticker".ljust(10), "Last".ljust(10), "Change".ljust(10), "% Change".ljust(10), "MACD Buy?".ljust(10),
            "MFI".ljust(10), "VZO".ljust(10), "Stochastic")
        print("{:<30}".format("–" * 70))

        losers = self.api.polygon.gainers_losers("losers")

        res = []
        for symbol in range(len(losers)):

            ticker = losers[symbol].ticker
            bars = self.api.get_barset(ticker, "1D", after=self.backdate)
            dataframe = self.api.extract_bar_data(bars, ticker)

            # sell signals
            try:
                macd_signal = TS.macd_sell(dataframe)
                mfi_signal = TS.mfi_sell(dataframe)
                vzo_signal = TS.vzo_sell(dataframe)
                stoch_signal = TS.stoch_sell(dataframe)
            except TSError:
                raise TSError("[!] Failed to compute one or more expected sell signals.")

            print(self.api.polygon.gainers_losers("losers")[symbol].ticker.ljust(10),
                "${:.2f}".format(self.api.polygon.gainers_losers("losers")[symbol].lastTrade["p"]).ljust(10),
                "${:.2f}".format(self.api.polygon.gainers_losers("losers")[symbol].todaysChange).ljust(10),
                "{:.2f}%".format(self.api.polygon.gainers_losers("losers")[symbol].todaysChangePerc).ljust(10),
                str(macd_signal).ljust(10),
                str(mfi_signal).ljust(10),
                str(vzo_signal).ljust(10),
                str(stoch_signal).ljust(10)
            )
            res.append(self.api.polygon.gainers_losers("losers")[symbol])
        return res

    def _filter_undervalued(self):
        """
            https://medium.com/datadriveninvestor/how-i-use-this-free-api-to-find-undervalued-stocks-6574b9a3f2fe

                and

            https://medium.com/automation-generation/trading-on-the-edge-how-this-free-api-helps-me-find-undervalued-stocks-7ec7b904ee37
        """
        raise NotImplementedError

    def _filter_overvalued(self):
        raise NotImplementedError

    def evaluate_candlestick(self, asset, barcount):
        """Return the candlestick pattern and dataframe of an asset if a bullish or bearish pattern is detected among the last three closing prices.

            Bullish patterns: hammer, inverseHammer
            Bearish patterns: bullishEngulfing, piercingLine, morningStar, threeWhiteSoldiers

        :param asset:
        :param barcount:
        :return:
        """
        if not asset or asset is None:
            raise ValueError("[!] Unable to evaluate a None asset.")

        barset = self.get_barset(asset.symbol, "1D", self.backdate)
        if barset is None:
            raise DataframeException("[!] Invalid barset -- cannot be None.")

        # if num_bars(barset[asset.symbol], barcount) is False:
        #     raise DataframeException("[!] Insufficient data.")

        df = self.extract_bar_data(barset, asset.symbol)

        # evaluate candlestick direction
        candle, pattern = self.candle_pattern_direction(df)
        if candle is not None:
            return df, candle, pattern
        else:
            raise CandlestickException("[!] Pattern not detected.")

    def bullish_candlesticks(self, barcount=64, poolsize=5):
        """Return assets with a bullish pattern of closing prices over a given period.

        :param barcount:
        :param poolsize:
        :return:
        """
        self.bulls = self._filter_bullish_assets(self.tradeable_assets, fname=inspect.stack()[0][3], barcount=barcount, poolsize=poolsize)

        return self.bulls

    def bearish_candlesticks(self, barcount=64, poolsize=5):
        """Return assets with a bearish pattern of closing prices over a given period.

        :param barcount:
        :param poolsize:
        :return:
        """
        self.bears = self._filter_bearish_assets(self.tradeable_assets, fname=inspect.stack()[0][3], barcount=barcount, poolsize=poolsize)

        return self.bears

    def top_gainers(self):
        """Return assets with a bullish pattern of closing prices over a given period.

        :return:
        """
        self.top_gainers = self._filter_top_gainers()

        return self.top_gainers

    def top_losers(self):
        """Return assets with a bearish pattern of closing prices over a given period.

        :return:
        """
        self.top_losers = self._filter_top_losers()

        return self.top_losers

    def undervalued(self):
        raise NotImplementedError

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

        print("[-] Going through assets looking for firms with recent SEC filings")
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
            print("[!] No recent filings found for {}. Looking back 2 weeks".format(asset.symbol))
            backdate = time_formatter(time.time() - (604800 * 2), time_format="%Y-%m-%d")
            filings = self.ei.get_sec_filings(asset.symbol, backdate, date, form_type=form_type)

        if filings["total"] is 0:
            print("[!] No filings found. Looking back 4 weeks")
            backdate = time_formatter(time.time() - (604800 * 4), time_format="%Y-%m-%d")
            filings = self.ei.get_sec_filings(asset.symbol, backdate, date, form_type=form_type)

        if filings["total"] > 0:
            print("[+] Added:", asset.symbol, " symbols:", len(self.recent_filings.keys()) + 1)
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

    def populate(self):

        self.get_assets()
        self.extract_tradeable_assets(self.raw_assets)
