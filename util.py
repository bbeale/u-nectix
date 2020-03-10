#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandas.io.json import json_normalize
from pandas.errors import EmptyDataError
from datetime import date
import pandas as pd
import numpy as np
import configparser
import argparse
import time
import json
import os


def time_from_timestamp(time_stamp, time_format=None):
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


def time_from_datetime(dt):
    if dt is None:
        raise ValueError
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f-04:00')


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


def parse_configs():
    parser = configparser.ConfigParser()
    try:
        parser.read(os.path.relpath("config.ini"))
    except FileExistsError as error:
        raise error
    else:
        return parser


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--algorithm",
        type=str,
        required=False,
        help="the algorithm we want to trade with -- must be a valid file in the algos directory")
    parser.add_argument("-b", "--backtest",
        required=False,
        action="store_true",
        help="run in backtest mode if true, otherwise run in live mode")
    parser.add_argument("-c", "--crypto",
        required=False,
        action="store_true",
        help="if true, trade cryptocurrency instead of stocks using the Kraken exchange.")
    parser.add_argument("-f", "--forex",
        required=False,
        action="store_true",
        help="if true, trade forex instead of stocks using the Kraken exchange.")
    parser.add_argument("-tp", "--testperiods",
        type=int,
        required=False,
        help="number of periods to backtest")
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
    return parser.parse_args()
