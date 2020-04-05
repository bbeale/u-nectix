#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.asset_selector import AssetSelector, AssetValidationException
from src.broker import BrokerException
from algos import BaseAlgo

from util import time_from_datetime
from datetime import datetime, timedelta
from pytz import timezone
from finta import TA
import pandas as pd


class Algorithm(AssetSelector, BaseAlgo):

    def __init__(self, broker, cli_args, stocktwits_key=None):
        super().__init__(broker=broker, cli_args=cli_args, edgar_token=None)
        # self.stocktwits = REST(api_key=stocktwits_key)  # setting api key to None for now because I'm not using authenticated endpoints

    def bullish_sentiment(self, backtest=False, bt_offset=None):
        if backtest:
            if not bt_offset or bt_offset is None:
                raise AssetValidationException("[!] Must specify a number of periods to offset if backtesting.")
            limit = bt_offset
        else:
            limit = 1000

        if not self.poolsize or self.poolsize is None or self.poolsize is 0:
            raise AssetValidationException("[!] Invalid pool size.")

        self.portfolio = []

        # sentiment calculation from StockTwits and Twitter
        trending_equities = self.stocktwits.trending_equities()

        for ass in trending_equities["symbols"]:

            ass = self.broker.get_asset(ass["symbol"])
            if ass is None or not ass.tradable or not ass.easy_to_borrow:
                continue

            df = self.broker.get_barset_df(ass.symbol, self.period, limit=limit)
            # df = self.broker.api.get_barset(ass.symbol, self.period, limit=1000).df
            # print(dir(df))
            # guard clauses to make sure we have enough data to work with
            if df is None or len(df) != limit:
                continue

            # throw it away if the price is out of our min-max range
            close = df["close"].iloc[-1]
            if close > self.max_stock_price or close < self.min_stock_price:
                continue

            message_texts = []
            bull_field_count = 0
            stocktwits_posts = self.stocktwits.streams_symbol(ass.symbol)
            for p in stocktwits_posts["messages"]:
                if p["entities"]["sentiment"] is not None:
                    bull_field_count += 1
                else:
                    # get sentiment of the text
                    message_texts.append(p["body"])

            message_texts = " ".join(message_texts)
            message_texts = message_texts.strip("  ")

            bull_field_score = (bull_field_count / len(stocktwits_posts["messages"])) * 100
            # print(dir(self))
            sentiment = self.sentiment_analyzer.get_sentiment(message_texts)

            # https://alpaca.markets/docs/api-documentation/api-v2/market-data/#polygon-integration

            self.portfolio.append(ass.symbol)
            if len(self.portfolio) >= self.poolsize:
                # exit the filter process
                break

    def get_ratings(self, algo_time=None, window_size=5):
        pass

    def portfolio_allocation(self, data, cash):
        pass

    def total_asset_value(self, positions, date):
        pass

def run(broker, args):

    if not broker or broker is None:
        raise BrokerException("[!] A broker instance is required.")
    else:
        broker = broker

    if args.algorithm is None:
        args.algorithm = "bullish_sentiment"
    if args.testperiods is None:
        args.testperiods = 30

    if args.cash is not None and type(args.cash) == float:
        cash = args.cash
    else:
        cash = float(broker.cash)

    if args.risk_pct is not None and type(args.risk_pct) in [int, float]:
        risk_pct = args.risk_pct
    else:
        risk_pct = .10

    # initial trade state
    starting_amount = cash
    risk_amount = broker.calculate_tolerable_risk(cash, risk_pct)
    algorithm = Algorithm(broker, args)

    symbols = algorithm.portfolio
    print("[*] Trading assets: {}".format(",".join(symbols)))

    if args.backtest:
        print("Do backtesty stuff")
    else:
        print("Do live stuff")