#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.sentiment_analysis import SentimentAnalysis, SentimentAnalysisException
from src.edgar_interface import EdgarInterface
from py_trade_signal.macd import MacdSignal
from py_trade_signal.mfi import MfiSignal
from py_trade_signal.obv import ObvSignal
from py_trade_signal.rsi import RsiSignal
from py_trade_signal.vzo import VzoSignal
from datetime import datetime, timedelta
from util import time_from_datetime
from broker.broker import Broker
from argparse import Namespace
from pytz import timezone
import pandas as pd


class AssetException(Exception):
    pass


class AssetValidationException(ValueError):
    pass


class DataframeException(AssetException):
    pass


class AssetSelector:

    def __init__(self, broker: Broker, cli_args: Namespace, edgar_token: str = None):
        """Initialize the asset selector with an optional edgar token

        TODO: Incorporate Twitter api and trade signals

        TODO:
        https://www.investopedia.com/articles/active-trading/092315/5-most-powerful-candlestick-patterns.asp
        https://www.daytrading.com/patterns

        TODO: Stocktwits!
        https://api.stocktwits.com/developers/docs/api

        https://pythondata.com/stationary-data-tests-for-time-series-forecasting/

        TODO: Multithread the selection process
        https://towardsdatascience.com/multithreading-in-python-for-finance-fc1425664e74

        TODO: Predictive power score
        https://towardsdatascience.com/rip-correlation-introducing-the-predictive-power-score-3d90808b9598

        :param broker:
        :param cli_args:
        :param edgar_token:
        """
        if not broker or broker is None:
            raise AssetValidationException('[!] A Broker instance is required.')

        self.now = datetime.now(timezone('EST'))

        if cli_args.backtest is not None:
            self.backtesting = True
            self.offset = cli_args.testperiods
            self.beginning = self.now - timedelta(days=self.offset)
            self.backtest_beginning = self.beginning - timedelta(days=self.offset)
        else:
            self.backtesting = False

        # assume the presence of crypto or forex arg means that's what we're trading
        if cli_args.crypto is not None and cli_args.crypto:
            self.asset_class = 'crypto'
        elif cli_args.forex is not None and cli_args.forex:
            self.asset_class = 'forex'
        else:
            self.asset_class = 'equity'

        if cli_args.period is not None:
            self.period = cli_args.period
        else:
            self.period = '1D'

        if cli_args.max is not None and type(cli_args.max) == int:
            self.max_stock_price = cli_args.max
        else:
            self.max_stock_price = 50

        if cli_args.min is not None and type(cli_args.min) == int:
            self.min_stock_price = cli_args.min
        else:
            self.min_stock_price = 0

        if 'bear' in cli_args.algorithm or 'short' in cli_args.algorithm:
            self.shorts_wanted = True
        else:
            self.shorts_wanted = False

        if cli_args.poolsize is not None:
            self.poolsize = cli_args.poolsize
        else:
            self.poolsize = 5

        self.broker = broker

        if edgar_token is not None:
            self.edgar_token = edgar_token
            self.ei = EdgarInterface(self.edgar_token)

        self.algorithm = cli_args.algorithm
        self.tradeable_assets = None
        self.recent_filings = None
        self.assets_by_filing = None
        self.portfolio = None

        # setting api key to None for now because I'm not using authenticated endpoints
        # self.stocktwits = REST(api_key=None)

        self.sentiment_analyzer = SentimentAnalysis()

        # init stage two:
        # self.get_assets(self.asset_class, self.algorithm)
        self.get_assets(self.asset_class)

    def get_assets(self, asset_class: str) -> None:   # , algorithm: str) -> None:
        """ Second method of two stage init process. """
        if asset_class == 'equity':
            raw_assets = self.broker.get_assets()
            if self.shorts_wanted:
                self._shortable(raw_assets)
            else:
                self._longable(raw_assets)
        else:
            raise NotImplementedError('[!] Crypto and forex asset trading is coming soon.')

    def _longable(self, asset_list: list, limit: int = 1000) -> None:
        """Scrub the list of assets from the Alpaca API response and get just the longable stocks we can trade.

        :param asset_list: list
        :param limit: int
        :return: None
        """
        self.tradeable_assets = [a for a in asset_list if a.tradable and a.marginable]

        self.portfolio = []
        for ass in self.tradeable_assets:
            if len(self.portfolio) >= self.poolsize:
                # exit the filter process -- we have all the stocks we want
                return

            if self.backtesting:
                start = time_from_datetime(self.backtest_beginning)
                end = time_from_datetime(self.beginning)
            else:
                start = time_from_datetime(self.beginning)
                end = time_from_datetime(self.now)

            # get the dataframe
            df = self.broker.get_asset_df(ass.symbol, self.period, limit=limit, start=start, end=end)

            # guard clauses to make sure we have enough data to work with
            if df is None or df.empty:
                continue

            # is the most recent date in the data frame the end date?
            df_end_date = str(df.iloc[-1].name).split(' ')[0]
            # time delta between df_end_date and end
            bt_end = datetime.strptime(end.split('T')[0], '%Y-%m-%d')
            df_end = datetime.strptime(df_end_date, '%Y-%m-%d')
            datediff = bt_end - df_end
            # if the last available data is older than 7 days, move on
            has_end_date = abs(datediff.days) < 7
            if not has_end_date:
                continue

            # throw it away if the price is out of our min-max range
            close = df["close"].iloc[-1]
            if close > self.max_stock_price or close < self.min_stock_price:
                continue

            # trade signal init
            macd_sig = MacdSignal(df)
            mfi_sig = MfiSignal(df)
            obv_sig = ObvSignal(df)
            rsi_sig = RsiSignal(df)
            vzo_sig = VzoSignal(df)

            if macd_sig.buy() or mfi_sig.buy() or obv_sig.buy() or rsi_sig.buy() or vzo_sig.buy():
                self.portfolio.append(ass)

    def _shortable(self, asset_list: list, limit: int = 1000) -> None:
        """Scrub the list of assets from the Alpaca API response and get just the short stocks we can trade.

        :param asset_list: list
        :param limit: int
        :return: None
        """
        self.tradeable_assets = [a for a in asset_list if
                                 a.tradable and a.shortable and a.marginable and a.easy_to_borrow]
        self.portfolio = []
        for ass in self.tradeable_assets:
            if len(self.portfolio) >= self.poolsize:
                # exit the filter process -- we have all the stocks we want
                return

            if self.backtesting:
                start = time_from_datetime(self.backtest_beginning)
                end = time_from_datetime(self.beginning)
            else:
                start = time_from_datetime(self.beginning)
                end = time_from_datetime(self.now)

            # get the dataframe
            df = self.broker.get_asset_df(ass.symbol, self.period, limit=limit, start=start, end=end)

            # guard clauses to make sure we have enough data to work with
            if df is None or df.empty:
                continue

            # is the most recent date in the data frame the end date?
            df_end_date = str(df.iloc[-1].name).split(' ')[0]
            # time delta between df_end_date and end
            bt_end = datetime.strptime(end.split('T')[0], '%Y-%m-%d')
            df_end = datetime.strptime(df_end_date, '%Y-%m-%d')
            datediff = bt_end - df_end
            # if the last available data is older than 7 days, move on
            has_end_date = abs(datediff.days) < 7
            if not has_end_date:
                continue

            # throw it away if the price is out of our min-max range
            close = df["close"].iloc[-1]
            if close > self.max_stock_price or close < self.min_stock_price:
                continue

            # trade signal init
            macd_sig = MacdSignal(df)
            mfi_sig = MfiSignal(df)
            obv_sig = ObvSignal(df)
            rsi_sig = RsiSignal(df)
            vzo_sig = VzoSignal(df)

            if macd_sig.sell() or mfi_sig.sell() or obv_sig.sell() or rsi_sig.sell() or vzo_sig.sell():
                self.portfolio.append(ass)

    def candle_pattern_direction(self, dataframe: pd.DataFrame) -> str:
        """Given a series, get the candlestick pattern of the last 3 periods.

        :param dataframe:
        :return:
        """
        pattern = self._pattern(dataframe.iloc[-3], dataframe.iloc[-2], dataframe.iloc[-1])
        direction = None

        if pattern in ['hammer', 'inverseHammer']:
            direction = 'bull'

        if pattern in ['bullishEngulfing', 'piercingLine', 'morningStar', 'threeWhiteSoldiers']:
            direction = 'bear'

        return direction

    @staticmethod
    def _pattern(c1: pd.Series, c2: pd.Series, c3: pd.Series) -> str:
        """Pilfered from Alpaca Slack channel

        :param c1:
        :param c2:
        :param c3:
        :return:
        """
        pattern = None
        # LOCH bullish
        if c1.low < c1.open < c1.close <= c1.high and c1.high - c1.close < c1.open - c1.low and c1.close - c1.open < c1.open - c1.low:
            pattern = 'hammer'
        if c1.low <= c1.open < c1.close < c1.high and c1.high - c1.close > c1.open - c1.low and c1.close - c1.open < c1.high - c1.close:
            pattern = 'inverseHammer'
        # LCOH bearish
        if c2.low < c2.close < c2.open < c2.high and c1.low <= c1.open < c1.close < c1.high and c1.open < c2.close and c1.close - c1.open > c2.open - c2.close:
            pattern = 'bullishEngulfing'
        if c2.low < c2.close < c2.open < c2.high and c1.low <= c1.open < c1.close < c1.high and c1.open < c2.close and c1.close > c2.close + (
                c2.open - c2.close) / 2:
            pattern = 'piercingLine'
        if c3.low < c3.close < c3.open < c3.high and c1.low <= c1.open < c1.close < c1.high and abs(
            c2.open - c2.close) < abs(c3.open - c3.close) and abs(c2.open - c2.close) < abs(c1.open - c1.close):
            pattern = 'morningStar'
        if c3.low <= c3.open < c3.close < c3.high and c2.low <= c2.open < c2.close < c2.high and c1.low <= c1.open < c1.close < c1.high and c3.close <= c2.open and c2.close <= c1.open:
            pattern = 'threeWhiteSoldiers'
        return pattern
