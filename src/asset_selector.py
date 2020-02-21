#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import time_formatter, num_bars
from src.edgar_interface import EdgarInterface
import json
import time


class AssetSelector:

    def __init__(self, broker, cli_args, edgar_token=None, poolsize=5):
        """Initialize the asset selector with an optional edgar token

        TODO: Incorporate Twitter api and trade signals

        :param broker:
        :param edgar_token:
        """
        if not broker or broker is None:
            raise AssetValidationException("[!] A Broker instance is required.")

        if cli_args.period is not None:
            self.period = cli_args.period
        else:
            self.period = "1D"

        if cli_args.max is not None and type(cli_args.max) == int:
            self.max_stock_price = cli_args.max
        else:
            self.max_stock_price = 50

        if cli_args.min is not None and type(cli_args.min) == int:
            self.min_stock_price = cli_args.min
        else:
            self.min_stock_price = 5

        if "short" in cli_args.mode or "long" in cli_args.mode:
            self.shorts_wanted = True

        self.broker = broker

        if edgar_token is not None:
            self.edgar_token = edgar_token
            self.ei = EdgarInterface(self.edgar_token)

        self.poolsize = poolsize
        self.selection_method = cli_args.selection_method
        self.raw_assets = None
        self.tradeable_assets = None
        self.recent_filings = None
        self.assets_by_filing = None
        self.trading_assets = None

        # init stage two:
        self._populate_assets()

    def _raw_assets(self):
        """Get assets from Alpaca API and assign them to self.raw_assets."""
        self.raw_assets = self.broker.get_assets()

    def _tradeable_assets(self, asset_list, short=False):
        """Scrub the list of assets from the Alpaca API response and get just the ones we can trade.

        :param asset_list:
        :return:
        """
        if not asset_list or asset_list is None or len(asset_list) is 0:
            raise AssetValidationException("[!] Invalid asset_list.")
        if short:
            self.tradeable_assets = [a for a in asset_list if
                                     a.tradable and a.shortable and a.marginable and a.easy_to_borrow]
        else:
            self.tradeable_assets = [a for a in asset_list if a.tradable and a.marginable]

    def _populate_assets(self):
        """ Second method of two stage init process. """
        self._raw_assets()
        self._tradeable_assets(self.raw_assets)
        self._assets_to_trade()

    def _assets_to_trade(self):
        """
        Populate tradeable assets based on CLI arg. This will not scale as I add more selection (sentiment, SEC) methods.
        """
        if not self.selection_method or self.selection_method is None or self.selection_method == "bullish_candlestick":
            self.bullish_candlesticks()
        elif self.selection_method == "bearish_candlestick":
            self.bearish_candlesticks()
        elif self.selection_method == "top_gainers":
            self.top_gainers()
        elif self.selection_method == "top_losers":
            self.top_losers()

        # todo - set trading_algorithm based on new cli arg for selection method. Default to bullish_candlesticks if None

        elif self.shorts_wanted:
            self.bearish_candlesticks()
        # todo - implement more of these and provide a more dynamic way to choose
        else:
            raise AssetException("[!] Unable to get assets by trading algorithm/strategy.")

    @staticmethod
    def _candlestick_patterns(c1, c2, c3):
        """Pilfered from Alpaca Slack channel

        :param c1:
        :param c2:
        :param c3:
        :return:
        """
        if c1 is None or c2 is None or c3 is None:
            raise AssetValidationException("[!] Must provide valid candlestick values to obtain a pattern.")

        pattern = None
        # LOCH bullish
        if c1.low < c1.open < c1.close <= c1.high and c1.high - c1.close < c1.open - c1.low and c1.close - c1.open < c1.open - c1.low:
            pattern = "hammer"
        if c1.low <= c1.open < c1.close < c1.high and c1.high - c1.close > c1.open - c1.low and c1.close - c1.open < c1.high - c1.close:
            pattern = "inverseHammer"
        # LCOH bearish
        if c2.low < c2.close < c2.open < c2.high and c1.low <= c1.open < c1.close < c1.high and c1.open < c2.close and c1.close - c1.open > c2.open - c2.close:
            pattern = "bullishEngulfing"
        if c2.low < c2.close < c2.open < c2.high and c1.low <= c1.open < c1.close < c1.high and c1.open < c2.close and c1.close > c2.close + (
                c2.open - c2.close) / 2:
            pattern = "piercingLine"
        if c3.low < c3.close < c3.open < c3.high and c1.low <= c1.open < c1.close < c1.high and abs(
            c2.open - c2.close) < abs(c3.open - c3.close) and abs(c2.open - c2.close) < abs(c1.open - c1.close):
            pattern = "morningStar"
        if c3.low <= c3.open < c3.close < c3.high and c2.low <= c2.open < c2.close < c2.high and c1.low <= c1.open < c1.close < c1.high and c3.close <= c2.open and c2.close <= c1.open:
            pattern = "threeWhiteSoldiers"
        return pattern

    def candle_pattern_direction(self, dataframe):
        """Given a series, get the candlestick pattern of the last 3 periods.

        :param dataframe:
        :return:
        """
        if dataframe is None:
            raise DataframeException("[!] Dataframe cannot be None.")

        pattern = self._candlestick_patterns(dataframe.iloc[-3], dataframe.iloc[-2], dataframe.iloc[-1])
        direction = None

        if pattern in ["hammer", "inverseHammer"]:
            direction = "bull"

        if pattern in ["bullishEngulfing", "piercingLine", "morningStar", "threeWhiteSoldiers"]:
            direction = "bear"

        return direction

    def bullish_candlesticks(self):
        """
        Given a list of assets, evaluate which ones are bullish and return a sample of each.
        """
        if not self.poolsize or self.poolsize is None or self.poolsize is 0:
            raise AssetValidationException("[!] Invalid pool size.")

        self.trading_assets = []

        for ass in self.tradeable_assets:
            """ The extraneous stuff that currently happens before the main part of evaluate_candlestick """
            limit = 1000
            df = self.broker.get_barset_df(ass.symbol, self.period, limit=limit)

            # guard clauses to make sure we have enough data to work with
            if df is None or len(df) != limit:
                continue

            # throw it away if the price is out of our min-max range
            close = df["close"].iloc[-1]
            if close > self.max_stock_price or close < self.min_stock_price:
                continue

            pattern = self.candle_pattern_direction(df)
            if pattern in ["bear", None]:
                continue

            if pattern is "bull":
                # add the current symbol the list of symbols
                self.trading_assets.append(ass.symbol)
                if len(self.trading_assets) >= self.poolsize:
                    # exit the filter process
                    break

    def bearish_candlesticks(self):
        """
        Given a list of assets, evaluate which ones are bearish and return a sample of each.
        """
        if not self.poolsize or self.poolsize is None or self.poolsize is 0:
            raise AssetValidationException("[!] Invalid pool size.")

        self.trading_assets = []

        for ass in self.tradeable_assets:
            limit = 1000
            df = self.broker.get_barset_df(ass.symbol, self.period, limit=limit)
            if df is None or len(df) != limit:
                continue

            pattern = self.candle_pattern_direction(df)
            if pattern in ["bull", None]:
                continue

            if pattern is "bear":
                # add the current symbol to the list of symbols
                self.trading_assets.append(ass.symbol)
                if len(self.trading_assets) >= self.poolsize:
                    # exit the filter process
                    break

    def top_gainers(self):
        """
        Use Polygon endpoint to populate a watchlist of top "gainers".
        """
        if not self.poolsize or self.poolsize is None or self.poolsize is 0:
            raise AssetValidationException("[!] Invalid pool size.")

        self.trading_assets = []

        gainers = self.broker.api.polygon.gainers_losers()
        for symbol in range(len(gainers)):

            ticker = gainers[symbol].ticker
            ass = self.broker.get_asset(ticker)
            if ass is not None and ass.tradable and ass.easy_to_borrow:
                # add the current symbol to the list of symbols
                self.trading_assets.append(ass.symbol)
                if len(self.trading_assets) >= self.poolsize:
                    # exit the filter process
                    break

    def top_losers(self):
        """
        Use Polygon endpoint to populate a list of top "losers".
        """
        if not self.poolsize or self.poolsize is None or self.poolsize is 0:
            raise AssetValidationException("[!] Invalid pool size.")

        self.trading_assets = []

        losers = self.broker.api.polygon.gainers_losers("losers")
        for symbol in range(len(losers)):

            ticker = losers[symbol].ticker
            ass = self.broker.get_asset(ticker)
            if ass is not None and ass.tradable and ass.easy_to_borrow:
                # add the current symbol to the list of symbols
                self.trading_assets.append(ass.symbol)
                if len(self.trading_assets) >= self.poolsize:
                    # exit the filter process
                    break

    def undervalued(self):
        """
            https://medium.com/datadriveninvestor/how-i-use-this-free-api-to-find-undervalued-stocks-6574b9a3f2fe

                and

            https://medium.com/automation-generation/trading-on-the-edge-how-this-free-api-helps-me-find-undervalued-stocks-7ec7b904ee37
        """
        raise NotImplementedError

    def overvalued(self):
        raise NotImplementedError

    """ Interacting with the EDGAR API. Not sure how I want to approach this yet because I haven't 
        spent a ton of time here since those rate limit issues I was having. 

        TODO figure out a solution now that my API account works again
    """

    def sec_filings(self, barcount=64, poolsize=5, form_type="8-K", backdate=None):
        """Return tradeable asets with recent SEC filings.

        :param barcount:
        :param poolsize:
        :param form_type:
        :param backdate:
        :return:




        TODO: Move the code in these methods into callbaccks ^ mentioned above
        """
        if not self.edgar_token or self.edgar_token is None:
            raise NotImplementedError

        if not backdate or backdate is None:
            # backdate = time_formatter(time.time() - 604800, time_format="%Y-%m-%d")
            # using a longer window only for debugging purposes -- just to make sure I have results quickly
            backdate = time_formatter(time.time() - (604800 * 26), time_format="%Y-%m-%d")

        date = time_formatter(time.time(), time_format="%Y-%m-%d")

        # Filter the assets down to just those on NASDAQ.
        active_assets = self.broker.get_assets()
        assets = self._tradeable_assets(active_assets)

        print("[-] Going through assets looking for firms with recent SEC filings")
        for i in assets:

            self.get_filings(i, backdate=backdate, date=date, form_type=form_type)

            if len(self.recent_filings.keys()) >= poolsize:
                break
            else:
                continue

        self.tradeable_assets_by_filings(barcount)

        # return self.assets_by_filing

        raise NotImplementedError("[!] SEC parsing needs to be reworked.")

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

        raise NotImplementedError("[!] SEC parsing needs to be reworked.")

    def tradeable_assets_by_filings(self, barcount=64):
        """Populate tradeable assets based on discovered SEC filings.

        :return:
        """
        for i in self.recent_filings.keys():
            # I think I need my original 13 week window here for consistency with get_assets_by_candlestick_pattern
            backdate = time_formatter(time.time() - (604800 * 13))

            barset = self.broker.get_barset(i.symbol, "1D", backdate)

            if num_bars(barset[i.symbol], barcount) is False:
                continue

            df = self.broker.extract_bar_data(barset, i.symbol)
            self.assets_by_filing[i.symbol] = df

        raise NotImplementedError("[!] SEC parsing needs to be reworked.")


class AssetException(Exception):
    pass


class AssetValidationException(ValueError):
    pass


class CandlestickException(AssetException):
    pass


class DataframeException(AssetException):
    pass
