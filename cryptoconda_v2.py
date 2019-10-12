#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.asset_selector import AssetSelector
from src.indicators import Indicators
from src.edgar_interface import EdgarInterface
from src.twitter_interface import TwitterInterface
from src.sentiment_analysis import SentimentAnalysis as Sent
from src.predictor import Predictor

from alpaca_functions import (
    time_formatter,
    calculate_indicators_v2 as calculate_indicators,
    get_predictions,
    get_sentiment,
    bullish_candlestick_patterns,
    get_stuff_to_trade_v2,
    bullish_sequence,
    submit_buy_order
)

import alpaca_trade_api as tradeapi
import numpy as np
import configparser
import time
import sys
import os

config = configparser.ConfigParser()

try:
    config.read(os.path.relpath("config.ini"))
except FileExistsError as e:
    print("FileExistsError: {}".format(e))
    sys.exit(1)


alpaca_api = tradeapi.REST(
    base_url    = config["alpaca"]["APCA_API_BASE_URL"],
    key_id      = config["alpaca"]["APCA_API_KEY_ID"],
    secret_key  = config["alpaca"]["APCA_API_SECRET_KEY"],
    api_version = config["alpaca"]["VERSION"]
)

edgar_token = config["edgar"]["TOKEN"]


def algo():

    candlestickPatternStart = time_formatter(time.time() - 604800)

    today = time_formatter(time.time())
    start = time_formatter(time.time() - (604800 * 13))

    # get ticker to trade
    raw_data = get_stuff_to_trade_v2(candlestickPatternStart)

    securities = dict()

    for item in raw_data.keys():
        indicators = calculate_indicators(item, start)

        sentiment = get_sentiment(item)
        if sentiment == "positive":
            securities[item] = indicators

    for item in securities.items():
        if bullish_sequence(item[1]["macd"].iloc[-3], item[1]["macd"].iloc[-2], item[1]["macd"].iloc[-1]):
            if item[1]["macd"].iloc[-1] >= item[1]["signal"].iloc[-1]:
                print("buy!")
                submit_buy_order(item[0], "buy", "market", "ioc")

    print(".")


def run():

    global alpaca_api
    # initial trade state -- False means not currently trading anything
    trading = False

    # maybe it makes more sense to initialize the alpaca sdk here since multiple classes are callign it

    assets      = AssetSelector(alpaca_api).get_stuff_to_trade_v2()
    indicators  = Indicators(alpaca_api, assets).get_indicators()
    edgar       = EdgarInterface(edgar_token, indicators).get_edgar_signals()
    twitter     = TwitterInterface()    # indicators=indicators)
    sentiment   = Sent()              # indicators=indicators)
    predictions = Predictor()       # indicators=indicators)

    # calculate trade decision
    # use data from object instances

    if trading is True:
        submit_buy_order("ticker", "buy", "market", "ioc")


def main():
    """Run the algorithm."""
    run()


if __name__ == "__main__":
    main()
