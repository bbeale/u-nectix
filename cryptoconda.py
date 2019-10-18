#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.asset_selector import AssetSelector
from src.indicators import Indicators
from src.edgar_interface import EdgarInterface
from src.twitter_interface import TwitterInterface
from src.sentiment_analysis import SentimentAnalysis as Sent
from src.predictor import Predictor
from util import submit_buy_order
import alpaca_trade_api as tradeapi
import configparser
import twitter
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

twitter_api = twitter.Api(
    config["twitter"]["CONSUMER_KEY"],
    config["twitter"]["CONSUMER_SECRET"],
    config["twitter"]["ACCESS_TOKEN_KEY"],
    config["twitter"]["ACCESS_TOKEN_SECRET"]
)

"""
    Right now, each of these three entry points below are using either different indicator or asset choosing strategies
    
    Run an algorithm by calling the function in main() 
"""


def algo_candlestick():

    global alpaca_api, twitter_api
    # initial trade state -- False means not currently trading anything
    trading = False

    # maybe it makes more sense to initialize the alpaca sdk here since multiple classes are callign it

    assets      = AssetSelector(alpaca_api, edgar_token=None).get_assets_by_candlestick_pattern()
    indicators  = Indicators(alpaca_api, assets).get_indicators()
    edgar       = EdgarInterface(edgar_token, indicators).get_edgar_signals()
    tweets      = TwitterInterface(twitter_api, indicators).get_ticker_tweets()
    sentiments  = Sent(indicators, tweets).get_sentiments()
    predictions = Predictor(indicators).get_securities_predictions()

    # calculate trade decision # TODO
    # use data from object instances

    if trading is True:
        submit_buy_order("ticker", "buy", "market", "ioc")


def algo_edgar():

    global alpaca_api, twitter_api, edgar_token
    # initial trade state -- False means not currently trading anything
    trading = False

    # maybe it makes more sense to initialize the alpaca sdk here since multiple classes are callign it

    assets      = AssetSelector(alpaca_api, edgar_token=edgar_token).get_assets_with_8k_filings()

    indicators  = Indicators(alpaca_api, assets).get_indicators()
    edgar       = EdgarInterface(edgar_token, indicators).get_edgar_signals()
    tweets      = TwitterInterface(twitter_api, indicators).get_ticker_tweets()
    sentiments  = Sent(indicators, tweets).get_sentiments()
    predictions = Predictor(indicators).get_securities_predictions()

    # calculate trade decision # TODO
    # use data from object instances

    if trading is True:
        submit_buy_order("ticker", "buy", "market", "ioc")


def algo_alt_indicators():

    global alpaca_api, twitter_api, edgar_token
    # initial trade state -- False means not currently trading anything
    trading = False

    assets      = AssetSelector(alpaca_api, edgar_token=None).get_assets_by_candlestick_pattern()
    indicators  = Indicators(alpaca_api, assets).g3t_m0ar_indicat0rszz()
    tweets      = TwitterInterface(twitter_api, indicators).get_ticker_tweets()
    sentiments  = Sent(indicators, tweets).get_sentiments()
    predictions = Predictor(indicators).get_securities_predictions()

    # trade decision here # TODO

    if trading is True:
        submit_buy_order("ticker", "buy", "market", "ioc")


def main():
    """Run the algorithm."""
    # algo_candlestick()
    # algo_edgar()
    algo_alt_indicators()


if __name__ == "__main__":
    main()
