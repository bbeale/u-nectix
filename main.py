#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.broker import Broker, BrokerException, BrokerValidationException
from algos import bullish_overnight_hold, bullish_overnight_crypto_hold
from src.krak_dealer import KrakDealer, KrakDealerException
from pykrakenapi.pykrakenapi import KrakenAPI, KrakenAPIError
from alpaca_trade_api.rest import REST, APIError
import krakenex
import configparser
import argparse
import sys
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--backtest",
        required=False,
        action="store_true",
        help="run in backtest mode if true, otherwise run in live mode")
    parser.add_argument("-c", "--crypto",
        required=False,
        action="store_true",
        help="if true, trade cryptocurrency instead of stocks using the Kraken exchange.")
    parser.add_argument("-d", "--days",
        type=int,
        required=False,
        help="number of days to backtest")
    parser.add_argument("-mx", "--max",
        type=float,
        required=False,
        help="max price per share we are willing to accept")
    parser.add_argument("-mn", "--min",
        type=float,
        required=False,
        help="min price per share we are willing to accept")
    parser.add_argument("-m", "--mode",
        type=str,
        required=False,
        help="long or short")
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

    # are we trading crypto?
    if args.crypto:
        print("[-] do stuff with Kraken")
        try:
            api = krakenex.API()
            k = KrakenAPI(api)
        except KrakenAPIError as error:
            raise error

        try:
            broker = KrakDealer(k)
        except KrakDealerException as error:
            raise error
        else:
            # is our account restricted from trading?
            if broker.trading_blocked:
                raise KrakDealerException("[!] Insufficient balances across coins or account is currently restricted from trading.")

        # how much money can we use to open new positions?
        print("[?] ${} is available in cash.".format(broker.trade_balance["tb"]))

        """Run the algorithm."""
        if args.mode is None:
            args.mode = 'long'
        if args.period is None:
            args.period = "1D"
        if args.days is None:
            args.days = 30

        bullish_overnight_crypto_hold.run(broker, args)

    else:
        # we must be trading stocks
        try:
            alpaca = REST(base_url=config["alpaca"]["APCA_API_BASE_URL"], key_id=config["alpaca"]["APCA_API_KEY_ID"],
                secret_key=config["alpaca"]["APCA_API_SECRET_KEY"], api_version=config["alpaca"]["VERSION"])
        except APIError as error:
            raise error

        try:
            broker = Broker(alpaca)
        except (BrokerException, BrokerValidationException, Exception) as error:
            raise error
        else:
            # is our account restricted from trading?
            if broker.trading_blocked:
                raise BrokerException("[!] Account is currently restricted from trading.")

        # how much money can we use to open new positions?
        print("[?] ${} is available in cash.".format(broker.cash))

        """Run the algorithm."""
        if args.mode is None:
            args.mode = 'long'
        if args.period is None:
            args.period = "1D"
        if args.selection_method is None:
            args.selection_method = "bullish_candlestick"
        if args.days is None:
            args.days = 30
        if args.max is None:
            args.max = 26
        if args.min is None:
            args.min = 6

        bullish_overnight_hold.run(broker, args)


if __name__ == "__main__":
    configuration = configparser.ConfigParser()
    arguments = parse_args()
    main(configuration, arguments)
