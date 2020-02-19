#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.broker import Broker, BrokerException, BrokerValidationException
from alpaca_trade_api.rest import REST, APIError
from algos import sample_algo
import configparser
import argparse
import sys
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--backtest",
        type=str,
        required=False,
        help="backtest")
    parser.add_argument("-m", "--mode",
        type=str,
        required=False,
        help="either \"long\" or \"short\"")
    parser.add_argument("-p", "--period",
        type=str,
        required=False,
        help="a period of time between candlestick bars, choices supported by Alpaca API are:  ")
    parser.add_argument("-r", "--records",
        type=int,
        required=False,
        help="number of records")
    parser.add_argument("-sm", "--selection_method",
        type=str,
        required=False,
        help="asset selection method - currently supports 'bullish_candlesticks', 'bearish_candlesticks', 'top_gainers', 'top_losers'")
    return parser.parse_args()


def main(config, args):

    try:
        config.read(os.path.relpath("config.ini"))
    except FileExistsError as e:
        print("[!] FileExistsError: {}".format(e))
        sys.exit(1)

    try:
        alpaca = REST(
            base_url    = config["alpaca"]["APCA_API_BASE_URL"],
            key_id      = config["alpaca"]["APCA_API_KEY_ID"],
            secret_key  = config["alpaca"]["APCA_API_SECRET_KEY"],
            api_version = config["alpaca"]["VERSION"]
        )
    except APIError as error:
        raise error

    # edgar_token = config["edgar"]["TOKEN"]

    try:
        broker = Broker(alpaca)
    except (BrokerException, BrokerValidationException, Exception) as error:
        raise error
    else:
        # is our account restricted from trading?
        if broker.trading_blocked:
            raise BrokerException("[!] Account is currently restricted from trading.")

    # how much money can we use to open new positions?
    print("[?] ${} is available as buying power.".format(broker.buying_power))

    """Run the algorithm."""
    if args.mode is None:
        args.mode = 'long'
    if args.period is None:
        args.period = "1D"
    if args.selection_method is None:
        args.selection_method = "bullish_candlestick"

    sample_algo.run(broker, args)


def backtest():
    raise NotImplementedError


if __name__ == "__main__":
    configuration = configparser.ConfigParser()
    arguments = parse_args()

    if arguments.backtest is not None and arguments.backtest:
        backtest()
    else:
        main(configuration, arguments)
