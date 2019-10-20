#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import date
import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import configparser
import sys
import os


# from empyrical import *
# import alphalens


config = configparser.ConfigParser()

try:
    config.read(os.path.relpath("config.ini"))
except FileExistsError as e:
    print("FileExistsError: {}".format(e))
    sys.exit(1)

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


def bullish_sequence(num1, num2, num3):
    """

    :param num1:
    :param num2:
    :param num3:
    :return:
    """
    return num1 >= num2 >= num3


def long_bullish_sequence(num1, num2, num3, num4, num5):
    """

    :param num1:
    :param num2:
    :param num3:
    :param num4:
    :param num5:
    :return:
    """
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
        pattern = "hammer"
    if c1.low <= c1.open < c1.close < c1.high and \
            c1.high - c1.close > c1.open - c1.low and \
            c1.close - c1.open < c1.high - c1.close:
        pattern = "inverseHammer"
    # LCOH bearish
    if c2.low < c2.close < c2.open < c2.high and \
            c1.low <= c1.open < c1.close < c1.high and \
            c1.open < c2.close and \
            c1.close - c1.open > c2.open - c2.close:
        pattern = "bullishEngulfing"
    if c2.low < c2.close < c2.open < c2.high and \
            c1.low <= c1.open < c1.close < c1.high and \
            c1.open < c2.close and \
            c1.close > c2.close + (c2.open - c2.close) / 2:
        pattern = "piercingLine"
    if c3.low < c3.close < c3.open < c3.high and \
            c1.low <= c1.open < c1.close < c1.high and \
            abs(c2.open - c2.close) < abs(c3.open - c3.close) and \
            abs(c2.open - c2.close) < abs(c1.open - c1.close):
        pattern = "morningStar"
    if c3.low <= c3.open < c3.close < c3.high and \
            c2.low <= c2.open < c2.close < c2.high and \
            c1.low <= c1.open < c1.close < c1.high and \
            c3.close <= c2.open and \
            c2.close <= c1.open:
        pattern = "threeWhiteSoldiers"
    return pattern


def get_returns(prices):
    """

    :param prices:
    :return:
    """
    return (prices-prices.shift(-1))/prices


def sort_returns(rets, num):
    """

    :param rets:
    :param num:
    :return:
    """
    ins = []
    outs = []
    for i in range(len(rets) - num):
        ins.append(rets[i:i + num].tolist())
        outs.append(rets[i + num])
    return np.array(ins), np.array(outs)


def submit_buy_order(ticker, transaction_side, ttype, time_in_force):
    """

    :param ticker:
    :param transaction_side:
    :param ttype:
    :param time_in_force:
    :return:
    """
    global api
    return api.submit_order(ticker, transaction_side, ttype, time_in_force)


def set_candlestick_df(bars):
    """Given a collection of candlestick bars, return a dataframe.

    Dataframe should contain keys:
        - time, open, high, low, close, volume

    :param bars:
    :return:
    """
    if not bars or bars is None:
        raise ValueError("Bars cannot be none")

    data = pd.DataFrame()
    data["time"]    = [bar.t for bar in bars if bar is not None]
    data["open"]    = [bar.o for bar in bars if bar is not None]
    data["high"]    = [bar.h for bar in bars if bar is not None]
    data["low"]     = [bar.l for bar in bars if bar is not None]
    data["close"]   = [bar.c for bar in bars if bar is not None]
    data["volume"]  = [bar.v for bar in bars if bar is not None]

    return data