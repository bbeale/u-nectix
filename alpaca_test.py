#!/usr/bin/env python
# -*- coding: utf-8 -*-
from statistics import mean
from datetime import date, timedelta
from finta import TA
import alpaca_trade_api as tradeapi
import twitter
import spacy
import nltk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import configparser
import pprint
import sys
import time
import os


config = configparser.ConfigParser()

try:
    config.read(os.path.relpath("config.ini"))
except FileExistsError as e:
    print("FileExistsError: {}".format(e))
    sys.exit(1)

pp = pprint.PrettyPrinter()

api = tradeapi.REST(
    base_url    = config["alpaca"]["APCA_API_BASE_URL"],
    key_id      = config["alpaca"]["APCA_API_KEY_ID"],
    secret_key  = config["alpaca"]["APCA_API_SECRET_KEY"],
    api_version = config["alpaca"]["VERSION"]
)


def time_formatter(time_stamp, time_format=None):
    """Return a formatted date in open market hours given a timestamp.

    :param time_stamp:
    :param time_format:
    :return:
    """
    if not time_stamp or time_stamp is None or type(time_stamp) is not float:
        raise ValueError
    if time_format is None:
        time_format = "%Y-%m-%dT09:30:00-04:00"
    return date.fromtimestamp(time_stamp).strftime(time_format)


def bullish_sequence(num1, num2, num3, num4, num5):
    return num1 >= num2 >= num3 >= num4 >= num5


def bullish_candlestick_patterns(c1, c2, c3):
    """Pilfered from Alpaca Slack channel

    :param c1:
    :param c2:
    :param c3:
    :return:
    """
    pattern = None
    # LOCH bullish
    if c1.low < c1.open < c1.close <= c1.high and \
            c1.high - c1.close < c1.open - c1.low and \
            c1.close - c1.open < c1.open - c1.low:
        pattern = 'hammer'
    if c1.low <= c1.open < c1.close < c1.high and \
            c1.high - c1.close > c1.open - c1.low and \
            c1.close - c1.open < c1.high - c1.close:
        pattern = 'inverseHammer'
    # LCOH bearish
    if c2.low < c2.close < c2.open < c2.high and \
            c1.low <= c1.open < c1.close < c1.high and \
            c1.open < c2.close and \
            c1.close - c1.open > c2.open - c2.close:
        pattern = 'bullishEngulfing'
    if c2.low < c2.close < c2.open < c2.high and \
            c1.low <= c1.open < c1.close < c1.high and \
            c1.open < c2.close and \
            c1.close > c2.close + (c2.open - c2.close) / 2:
        pattern = 'piercingLine'
    if c3.low < c3.close < c3.open < c3.high and \
            c1.low <= c1.open < c1.close < c1.high and \
            abs(c2.open - c2.close) < abs(c3.open - c3.close) and \
            abs(c2.open - c2.close) < abs(c1.open - c1.close):
        pattern = 'morningStar'
    if c3.low <= c3.open < c3.close < c3.high and \
            c2.low <= c2.open < c2.close < c2.high and \
            c1.low <= c1.open < c1.close < c1.high and \
            c3.close <= c2.open and \
            c2.close <= c1.open:
        pattern = 'threeWhiteSoldiers'
    return pattern


def write_barset_to_file(barset, ticker):
        datafile = os.path.relpath("data/{}_data_{}.csv".format(ticker, time.time()))
        with open(datafile, "w+") as df:
            df.write("time,open,high,low,close,volume,vol_avg,,is_bullish,macd,signal,macd_buy_sign,macd_pos_momentum,mfi,mfi_buy_sign,mfi_pos_momentum,stoch,stoch_buy_sign,stoch_pos_momentum,sentiment\n")
            for b in barset:
                df.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(b.t, b.o, b.c, b.h, b.l, b.v, 0,0,0,0,0,0,0,0,0,0,0,0,0))

        if type(datafile) is str and len(datafile) > 0:
            return datafile, ticker
        else:
            raise FileExistsError


def get_stuff_to_trade():
    """ Loops through all securities with volume data, grabs the best ones for trading according to the indicators

    :return vol_assets: list of dictionaries representing intraday, MACD, RSI, RoC, and stochastic oscillators
    """
    account                 = api.get_account()

    print("Account #:       {}".format(account.account_number))
    print("Currency:        {}".format(account.currency))
    print("Cash value:      ${}".format(account.cash))
    print("Buying power:    ${}".format(account.buying_power))
    print("DT count:        {}".format(account.daytrade_count))
    print("DT buying power: ${}".format(account.daytrading_buying_power))

    # Check if our account is restricted from trading.
    if account.trading_blocked:
        print("Account is currently restricted from trading.")

    # Check how much money we can use to open new positions.
    print("${} is available as buying power.".format(account.buying_power))

    active_assets = api.list_assets(status="active")

    # Filter the assets down to just those on NASDAQ.
    assets = [a for a in active_assets if a.exchange == "NASDAQ" and a.tradable and a.shortable and a.marginable and a.easy_to_borrow]
    assets_to_compare = {}
    for i in list(filter(lambda ass: ass.tradable is True, assets)):

        symbol = i.symbol
        today = time_formatter(time.time())
        start = time_formatter(time.time() - (604800 * 2))

        barset = api.get_barset(symbol, "1Min", after=start)
        # barset = api.get_barset("VRSK", "15Min", after=start)
        symbol_bars = barset[symbol]
        vmean = 0

        # Get trading volume
        volume = [bar.v for bar in symbol_bars if bar is not None]
        if volume is None:
            continue

        # And closing price
        closeprices = [bar.c for bar in symbol_bars if bar is not None]
        if closeprices is None:
            continue

        if len(volume) > 0:
            vmean = mean(volume)
        datafile = os.path.relpath("data/{}_data_{}.csv".format(symbol, time.time()))
        with open(datafile, "w+") as df:
            df.write("time,open,high,low,close,volume,vol_avg\n")
            for b in barset[symbol]:
                df.write("{},{},{},{},{},{},{}\n".format(b.t, b.o, b.c, b.h, b.l, b.v, vmean))

        if type(datafile) is str and len(datafile) > 0:
            return datafile, symbol
        else:
            raise FileExistsError


def calculate_indicators(d_file, ticker):
    """Calculating simple indicators for a long position. Or short? Haven't fully decided...

    :param d_file:
    :param ticker:
    :return:
    """
    if not d_file or d_file is None:
        raise FileNotFoundError("Invalid dataframe file")

    if not ticker or ticker is None:
        raise ValueError("Invalid ticker value")

    try:
        data = pd.read_csv(d_file)
    except OSError:
        raise OSError

    print(data["close"].iloc[-1], data["close"].iloc[-2], data["close"].iloc[-3])
    is_bullish = bullish_sequence(
        data["close"].iloc[-1],
        data["close"].iloc[-2],
        data["close"].iloc[-3],
        data["close"].iloc[-4],
        data["close"].iloc[-5]
    )
    ix = int(len(data) / 4)
    bullish_pattern = bullish_candlestick_patterns(data.iloc[-1], data.iloc[-2], data.iloc[-3])

    macd_buy_sign = False
    mfi_buy_sign = False
    stoch_buy_sign = False

    # get MACD
    macd = TA.MACD(data)
    _macds = macd["MACD"]
    _signals = macd["SIGNAL"]

    if macd.iloc[-1]["MACD"] > macd.iloc[-1]["SIGNAL"]:
        macd_buy_sign = True

    macd_10day_mean = macd.iloc[-ix:]["MACD"].mean()
    signal_10day_mean = macd.iloc[-ix:]["SIGNAL"].mean()

    macd_pos_momentum = bullish_sequence(
        _macds.iloc[-1],
        _macds.iloc[-2],
        _macds.iloc[-3],
        _macds.iloc[-4],
        _macds.iloc[-5]
    )

    macd_signal_pos_momentum = bullish_sequence(
        _signals.iloc[-1],
        _signals.iloc[-2],
        _signals.iloc[-3],
        _signals.iloc[-4],
        _signals.iloc[-5]
    )

    # get money flow index
    mfi = TA.MFI(data)

    if mfi.iloc[-1] <= 20:
        mfi_buy_sign = True

    mfi_10day_mean = mfi.iloc[-ix:].mean()

    mfi_pos_momentum = mfi.iloc[-1] >= mfi.iloc[-2] >= mfi.iloc[-3]

    # get stochastic oscillator
    stoch = TA.STOCH(data)

    if stoch.iloc[-1] <= 20:
        stoch_buy_sign = True

    stoch_10day_mean = stoch.iloc[-ix:].mean()

    stoch_pos_momentum = stoch.iloc[-1] >= stoch.iloc[-2] >= stoch.iloc[-3]

    td = dict()
    td["ticker"] = ticker
    td["is_bullish"] = is_bullish
    td["bullish_pattern"] = bullish_pattern
    # macd results
    td["data"] = data
    td["macd"] = _macds
    td["signal"] = _signals
    td["macd_buy_sign"] = macd_buy_sign
    td["macd_10day_mean"] = macd_10day_mean
    td["signal_10day_mean"] = signal_10day_mean
    td["macd_pos_momentum"] = macd_pos_momentum
    td["macd_signal_pos_momentum"] = macd_signal_pos_momentum
    # mfi results
    td["mfi"] = mfi
    td["mfi_buy_sign"] = mfi_buy_sign
    td["mfi_10day_mean"] = mfi_10day_mean
    td["mfi_pos_momentum"] = mfi_pos_momentum
    # stoch results
    td["stoch"] = stoch
    td["stoch_buy_sign"] = stoch_buy_sign
    td["stoch_10day_mean"] = stoch_10day_mean
    td["stoch_pos_momentum"] = stoch_pos_momentum

    if td and len(td.keys()) > 0:
        return td
    else:
        raise ValueError


def get_sentiment(ticker):
    # https://www.youtube.com/watch?v=EblHYC4EB_s&list=WL&index=3&frags=wn
    t_api = twitter.Api(config["twitter"]["CONSUMER_KEY"], config["twitter"]["CONSUMER_SECRET"], config["twitter"]["ACCESS_TOKEN_KEY"], config["twitter"]["ACCESS_TOKEN_SECRET"])

    results = t_api.GetSearch("{} stock".format(ticker), result_type="recent")

    result_dicts = [dict(created_at=time_formatter(float(result.created_at_in_seconds)), user=result.user.name, text=result.text) for result in results if "RT" not in result.text]

    texts = [res["text"] for res in result_dicts]
    text = "\n\n".join(texts)

    print(".")      # TODO: finish


def main():

    # raw_data, ticker = get_stuff_to_trade()
    # raw_data = os.path.relpath("data\\VRSK_test_data_9-2018-9-2019-1min.csv")         # 1min
    # raw_data = os.path.relpath("data/VRSK_test_data_9-20189-9-2019-15min.csv")        # 15min
    # raw_data = os.path.relpath("data/VRSK_test_data_fast.csv")                        # fast window
    raw_data = os.path.relpath("data/VRSK_test_data_short_window_minute_int.csv")       # fast long window
    ticker = "VRSK"
    indicators = calculate_indicators(raw_data, ticker)
    get_sentiment(ticker)


if __name__ == "__main__":
    main()
