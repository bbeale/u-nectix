#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandas.io.json import json_normalize
from pandas.errors import EmptyDataError
from datetime import date
import pandas as pd
import numpy as np
import time
import json
import os


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


def set_candlestick_df(bars):
    """Given a collection of candlestick bars, return a dataframe.

    Dataframe should contain keys:
        - time, open, high, low, close, volume

    :param bars:
    :return:
    """
    if not bars or bars is None:
        raise ValueError("Bars cannot be none")

    data            = pd.DataFrame(index=[bar.t for bar in bars if bar is not None])
    data["open"]    = [bar.o for bar in bars if bar is not None]
    data["high"]    = [bar.h for bar in bars if bar is not None]
    data["low"]     = [bar.l for bar in bars if bar is not None]
    data["close"]   = [bar.c for bar in bars if bar is not None]
    data["volume"]  = [bar.v for bar in bars if bar is not None]

    return data


def num_bars(barset, length):
    """Check the bar count to ensure uniform length for dataframe.

    Return True if the number of bars is equal to the target length, otherwise False.

    :param barset: a collection of bars (time + ohlcv format)
    :param length: target length to ensure
    :return boolean:
    """
    res = len(barset) == length
    if not res or res is False:
        res = len(barset) == length - 1
    return res


def logarithmic_scale(series):
    """Convert a series from a linear scale to a logarithmic scale.

    :param series:
    :return:
    """
    return np.log(series) - np.log(series.shift(1))


def convert_json_to_df(obj):
    """Convert JSON to DataFrame.

    :param: JSON
    :return: DataFrame
    """
    return json_normalize(json.loads(json.dumps(obj)))


def convert_obj_to_df(obj):
    """Convert Object to DataFrame.

    :param: Python Object
    :return: DataFrame
    """
    return json_normalize(json.loads(json.dumps(obj.__dict__)))


def convert_obj_list_to_df(obj):
    """Convert Object List to DataFrame.

    :param: Python Object
    :return: DataFrame
    """
    return json_normalize(json.loads(json.dumps([ob.__dict__ for ob in obj])))


def df2csv(dataframe, ticker):
    """Save the contents of a dataframe to a csv file in the data/ directory.

    File name will include the ticker (required arg) and current timestamp.

    :param dataframe:
    :param ticker:
    :return:
    """
    if dataframe is None:
        raise EmptyDataError("Dataframe cannot be empty.")
    if not ticker or ticker is None:
        raise ValueError("[!] Invalid ticker value.")

    datafile = os.path.relpath("data/{}_data_{}.csv".format(ticker, time.time()))

    try:
        dataframe.to_csv(datafile, index=False)
    except FileNotFoundError:
        print("[?] Retrying one directory level up.")
        datafile = os.path.relpath("../data/{}_data_{}.csv".format(ticker, time.time()))
        try:
            dataframe.to_csv(datafile, index=False)
        except FileNotFoundError:
            raise FileNotFoundError("[!] Unable to save dataframe to CSV file.")
    finally:
        print("[+] File saved:\t{}".format(datafile))


def calculate_tolerable_risk(balance, risk_pct):

    if not balance or balance is None or balance == 0:
        raise ValueError("[!] valid balance is required.")

    if not risk_pct or risk_pct is None or risk_pct == 0:
        raise ValueError("[!] risk_pct cannot be zero.")

    return float(balance * risk_pct)


def calculate_position_size(price, trading_balance, risk_pct=.10):
    """Given a stock price, available trading balance, and a risk percentage, calculate a position size for a trade.

    :param price:
    :param trading_balance:
    :param risk_pct:
    :return:
    """

    if not price or price is None:
        raise ValueError("[!] A price is required for this calculation.")

    if not trading_balance or trading_balance is None:
        raise ValueError("[!] A trading_balance is required for this calculation.")

    if risk_pct == 0:
        raise ValueError("[!] risk_pct cannot be zero.")

    return int(trading_balance * risk_pct / price)
