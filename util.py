#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import date
from pandas.io.json import json_normalize
from pandas.errors import EmptyDataError
import alpaca_trade_api as tradeapi
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


def submit_order(api_reference, ticker, qty, transaction_side, ttype, time_in_force):
    """Submit an order using a reference to the Alpaca API.

    :param api_reference: An instance of the Aplaca API
    :param ticker: Ticker symbol to trade
    :param qty: Number of shares to trade
    :param transaction_side: Buy or sell
    :param ttype: Order type (market, limit, stop, or stop_limit)
    :param time_in_force: day, gtc, opg, cls, ioc, or fok
    :return:
    """
    if not api_reference or api_reference is None:
        raise ValueError("Invalid API reference")

    if not ticker or ticker is None:
        raise ValueError("Invalid ticker")

    if qty is None or len(qty) < 1:
        raise ValueError("Invalid qty")

    if not transaction_side or transaction_side not in ["buy", "sell"]:
        raise ValueError("Invalid transaction_side")

    if not ttype or ttype not in ["market", "limit", "stop", "stop_limit"]:
        raise ValueError("Invalid ttype")

    if not time_in_force or time_in_force not in ["day", "gtc", "opg", "cls", "ioc", "fok"]:
        raise ValueError("Invalid time_in_force")

    try:
        result = api_reference.submit_order(ticker, qty, transaction_side, ttype, time_in_force)
    except tradeapi.rest.APIError:
        raise tradeapi.rest.APIError("[!] Unable to submit {} order for {}.".format(str(transaction_side), str(ticker)))
    else:
        return result

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
