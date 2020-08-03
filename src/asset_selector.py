#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.sentiment_analysis import SentimentAnalysis, SentimentAnalysisException
from src.edgar_interface import EdgarInterface
from datetime import datetime, timedelta
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

        if 'bear' in cli_args.algorithm:
            self.shorts_wanted = True

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
        self.get_assets(self.asset_class, self.algorithm)

    def get_assets(self, asset_class: str, algorithm: str) -> None:
        """ Second method of two stage init process. """
        if asset_class == 'equity':
            raw_assets = self._raw_equity_assets()
            self._tradeable_equity_assets(raw_assets, algorithm)
        else:
            raise NotImplementedError('[!] Crypto and forex asset trading is coming soon.')

    def _raw_equity_assets(self) -> list:
        """Get assets from Alpaca API and assign them to self.raw_assets."""
        return self.broker.get_assets()

    def _tradeable_equity_assets(self, asset_list: list, algorithm: str, short: bool = False) -> None:
        """Scrub the list of assets from the Alpaca API response and get just the ones we can trade.

        :param asset_list:
        :return:
        """
        if algorithm not in [item for item in dir(self) if '__' not in item]:
            raise AssetValidationException('[!] Unable to determine asset selector method in the context of AssetSelector')

        if short:
            self.tradeable_assets = [a for a in asset_list if
                                     a.tradable and a.shortable and a.marginable and a.easy_to_borrow]
        else:
            self.tradeable_assets = [a for a in asset_list if a.tradable and a.marginable]

        # populate our portfolio based on our trading algorithm
        selection_method = getattr(self, algorithm)

        if self.backtesting:
            selection_method(self.backtesting, self.offset)
        else:
            selection_method()

    @staticmethod
    def _candlestick_patterns(c1: pd.Series, c2: pd.Series, c3: pd.Series) -> str:
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

    def candle_pattern_direction(self, dataframe: pd.DataFrame) -> str:
        """Given a series, get the candlestick pattern of the last 3 periods.

        :param dataframe:
        :return:
        """
        pattern = self._candlestick_patterns(dataframe.iloc[-3], dataframe.iloc[-2], dataframe.iloc[-1])
        direction = None

        if pattern in ['hammer', 'inverseHammer']:
            direction = 'bull'

        if pattern in ['bullishEngulfing', 'piercingLine', 'morningStar', 'threeWhiteSoldiers']:
            direction = 'bear'

        return direction

    def get_asset_dataframe(self, asset, backtest: bool = False, limit: int = None):
        """

        :param asset:
        :param backtest:
        :param limit:
        :return:
        """
        if not asset or asset is None:
            raise AssetValidationException('[!] Invalid asset')
        if backtest:
            if self.offset is None:
                raise AssetValidationException('[!] Unable to backtest without an offset period.')
            now = datetime.now(timezone('EST'))
            beginning = now - timedelta(days=self.offset)
            df = self.broker.get_asset_df(asset.symbol, self.period, limit=limit, start=beginning, end=now)
        else:
            df = self.broker.get_asset_df(asset.symbol, self.period, limit=limit)
        return df
