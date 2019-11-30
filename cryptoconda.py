#!/usr/bin/env python
# -*- coding: utf-8 -*-
from algos import bullish_candlestick
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

trading_account = alpaca_api.get_account()

edgar_token = config["edgar"]["TOKEN"]

twitter_api = twitter.Api(
    config["twitter"]["CONSUMER_KEY"],
    config["twitter"]["CONSUMER_SECRET"],
    config["twitter"]["ACCESS_TOKEN_KEY"],
    config["twitter"]["ACCESS_TOKEN_SECRET"]
)


def main():

    # is our account restricted from trading?
    if trading_account.trading_blocked:
        print("Account is currently restricted from trading.")
        sys.exit(-1)

    # how much money can we use to open new positions?
    print("${} is available as buying power.".format(trading_account.buying_power))

    """Run the algorithm."""
    bullish_candlestick.run(alpaca_api)


if __name__ == "__main__":
    main()
