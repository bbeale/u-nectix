#!/usr/bin/env python
# -*- coding: utf-8 -*-
from algos import candlestick, edgar, simple_candlestick
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


def main():
    """Run the algorithm."""
    candlestick.run(alpaca_api)
    # edgar.run(alpaca_api, twitter_api, edgar_token)
    # simple_candlestick.run(alpaca_api)


if __name__ == "__main__":
    main()
