#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import date
from statistics import mean
from finta import TA
from lib.edgar import calculate_transaction_amount, download_xml, calculate_8k_transaction_amount
import alpaca_trade_api as tradeapi
import twitter
import spacy
import nltk
import tensorflow as tf
import numpy as np
import pandas as pd
import configparser
import requests
import pprint
import sys
import time
import os
import json


# from empyrical import *
# import alphalens


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

"""
> `python -m spacy download en_core_web_md`  
> `python -m spacy download en_core_web_lg`&emsp;&emsp;&ensp;*optional library*  
> `python -m spacy download en_vectors_web_lg`&emsp;*optional library*  

"""


nlp = spacy.load("en_vectors_web_lg")
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

sess = tf.InteractiveSession()


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
    return num1 >= num2 >= num3


def long_bullish_sequence(num1, num2, num3, num4, num5):
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


def get_stuff_to_trade_v2(backdate):

    account                 = api.get_account()
    # Check if our account is restricted from trading.
    if account.trading_blocked:
        print("Account is currently restricted from trading.")

    # Check how much money we can use to open new positions.
    print("${} is available as buying power.".format(account.buying_power))

    active_assets = api.list_assets(status="active")

    # Filter the assets down to just those on NASDAQ.
    assets = [a for a in active_assets if a.tradable and a.shortable and a.marginable and a.easy_to_borrow]
    bullish_to_compare = {}
    bearish_to_compare = {}
    for i in list(filter(lambda ass: ass.tradable is True, assets)):

        symbol = i.symbol
        start = backdate
        barset = api.get_barset(symbol, "1D", after=start)
        symbol_bars = barset[symbol]

        df = pd.DataFrame()
        df["time"] = [bar.t for bar in symbol_bars if bar is not None]
        df["open"] = [bar.o for bar in symbol_bars if bar is not None]
        df["high"] = [bar.h for bar in symbol_bars if bar is not None]
        df["low"] = [bar.l for bar in symbol_bars if bar is not None]
        df["close"] = [bar.c for bar in symbol_bars if bar is not None]
        df["volume"] = [bar.v for bar in symbol_bars if bar is not None]

        pattern = bullish_candlestick_patterns(df.iloc[-3], df.iloc[-2], df.iloc[-1])

        if pattern is None:
            continue

        if pattern in ["hammer", "inverseHammer"]:
            bullish_to_compare[symbol] = df

        if pattern in ["bullishEngulfing", "piercingLine", "morningStar", "threeWhiteSoldiers"]:
            bearish_to_compare[symbol] = df

        if len(bearish_to_compare) is 5 or len(bullish_to_compare) is 5:
            if len(bearish_to_compare) > len(bullish_to_compare):
                return bearish_to_compare
            elif len(bullish_to_compare) > len(bearish_to_compare):
                return bullish_to_compare


def get_stuff_to_trade(curdate, backdate):
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
        # today = time_formatter(time.time())
        # start = time_formatter(time.time() - (604800 * 2))
        today = curdate
        start = backdate
        barset = api.get_barset(symbol, "1D", after=start)
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


def calculate_indicators_v2(ticker, backdate):

    if not ticker or ticker is None:
        raise ValueError("Invalid ticker value")

    if not backdate or backdate is None:
        raise ValueError("Invalid backdate value")

    try:
        bars = api.get_barset(ticker, "1D", after=backdate)[ticker]
    except OSError:
        raise OSError

    data = pd.DataFrame()
    data["time"]    = [bar.t for bar in bars if bar is not None]
    data["open"]    = [bar.o for bar in bars if bar is not None]
    data["high"]    = [bar.h for bar in bars if bar is not None]
    data["low"]     = [bar.l for bar in bars if bar is not None]
    data["close"]   = [bar.c for bar in bars if bar is not None]
    data["volume"]  = [bar.v for bar in bars if bar is not None]

    print(data["close"].iloc[-1], data["close"].iloc[-2], data["close"].iloc[-3])

    # get MACD
    macd = TA.MACD(data)
    _macds = macd["MACD"]
    _signals = macd["SIGNAL"]

    # get money flow index
    mfi = TA.MFI(data)

    # get stochastic oscillator
    stoch = TA.STOCH(data)

    data["ticker"]  = ticker
    data["macd"]    = _macds
    data["signal"]  = _signals
    data["mfi"]     = mfi
    data["stoch"]   = stoch

    return data


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
        # data["close"].iloc[-4],
        # data["close"].iloc[-5]
    )
    ix = int(len(data) / 4)
    bullish_pattern = bullish_candlestick_patterns(data.iloc[-1], data.iloc[-2], data.iloc[-3])

    # get timestamps
    timestamps = data["time"]

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
        # _macds.iloc[-4],
        # _macds.iloc[-5]
    )

    macd_signal_pos_momentum = bullish_sequence(
        _signals.iloc[-1],
        _signals.iloc[-2],
        _signals.iloc[-3],
        # _signals.iloc[-4],
        # _signals.iloc[-5]
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

    data["ticker"] = ticker
    data["macd"] = _macds
    data["signal"] = _signals
    data["mfi"] = mfi
    data["stoch"] = stoch

    # td = dict()
    # td["is_bullish"] = is_bullish
    # td["bullish_pattern"] = bullish_pattern
    # macd results
    # td["data"] = data
    # td["macd_buy_sign"] = macd_buy_sign
    # td["macd_10day_mean"] = macd_10day_mean
    # td["signal_10day_mean"] = signal_10day_mean
    # td["macd_pos_momentum"] = macd_pos_momentum
    # td["macd_signal_pos_momentum"] = macd_signal_pos_momentum
    # mfi results
    # td["mfi_buy_sign"] = mfi_buy_sign
    # td["mfi_10day_mean"] = mfi_10day_mean
    # td["mfi_pos_momentum"] = mfi_pos_momentum
    # stoch results
    # td["stoch_buy_sign"] = stoch_buy_sign
    # td["stoch_10day_mean"] = stoch_10day_mean
    # td["stoch_pos_momentum"] = stoch_pos_momentum

    # if td and len(td.keys()) > 0:
    #     return td
    # else:
    #     raise ValueError

    return data


def get_sentiment(ticker):

    t_api = twitter.Api(
        config["twitter"]["CONSUMER_KEY"],
        config["twitter"]["CONSUMER_SECRET"],
        config["twitter"]["ACCESS_TOKEN_KEY"],
        config["twitter"]["ACCESS_TOKEN_SECRET"]
    )

    results = t_api.GetSearch("{} stock".format(ticker), result_type="recent")

    result_dicts = [dict(
        created_at  = time_formatter(float(result.created_at_in_seconds)),
        user        = result.user.name,
        text        = result.text
    ) for result in results if "RT" not in result.text]

    texts = [res["text"] for res in result_dicts]
    text = "\n\n".join(texts)

    text_polarity = sid.polarity_scores(text)

    if text_polarity["compound"] > 0:
        sentiment = "positive"

    else:
        sentiment = "negative"

    return sentiment


def get_edgar_score(dataframe, ticker):

    TOKEN = config["edgar"]["TOKEN"]

    # API endpoint
    BASE_URL = config["edgar"]["URL"]

    API = "{}?token={}".format(BASE_URL, TOKEN)

    # filter_8k = "ticker:(\"%s\") AND formType:(\"8-K\") AND filedAt:{2019-08-01 TO 2019-09-26}" % ticker
    filter_8k = "ticker:(\"%s\") AND formType:(\"8-K\")" % ticker
    sort = [{"filedAt": {"order": "desc"}}]
    start = 0
    size = 100

    payload = {
        "query": {"query_string": {"query": filter_8k}},
        "from": start,
        "size": size,
        "sort": sort
    }

    resp = requests.post(API, payload).text
    r_dict = json.loads(resp)
    signal = None
    total_traded = 0

    for item in r_dict["filings"]:
        xml = download_xml(item["linkToTxt"])
        # xml = bs_xml_parse(item["linkToTxt"])
        amount = calculate_transaction_amount(xml)
        total_traded += amount

        initial, post, percenttraded, majorshareholder = calculate_8k_transaction_amount(xml)

        print("# pre:\t\t", initial)
        print("# post:\t\t", post)
        print("% traded\t\t", percenttraded)

        if majorshareholder and initial > post:
            signal = "STRONGBEAR"

        elif not majorshareholder and initial > post:
            signal = "BEAR"

        elif majorshareholder and post > initial:
            signal = "STRONGBULL"

        elif not majorshareholder and initial > post:
            signal = "BULL"

        else:
            return "Unable to generate signal from SEC filings"

    if "edgar" not in dataframe.keys() or dataframe["edgar"] is None:
        dataframe["edgar"] = signal

    return dataframe


def risk_management():
    raise NotImplementedError


def get_returns(prices):
    return (prices-prices.shift(-1))/prices


def sort_returns(rets, num):
    ins = []
    outs = []
    for i in range(len(rets) - num):
        ins.append(rets[i:i + num].tolist())
        outs.append(rets[i + num])
    return np.array(ins), np.array(outs)


def get_predictions(data):

    data = data.astype(float)
    size = 50
    returns = get_returns(data)

    # pass one of the above into sort_returns
    ins, outs = sort_returns(returns, size)

    div = int(.8 * ins.shape[0])
    train_ins, train_outs = ins[:div], outs[:div]
    test_ins, test_outs = ins[div:], outs[div:]

    # sess = tf.InteractiveSession()
    x = tf.placeholder(tf.float32, [None, size])
    y_ = tf.placeholder(tf.float32, [None, 1])

    # we define trainable variables for our model
    W = tf.Variable(tf.random_normal([size, 1]))
    b = tf.Variable(tf.random_normal([1]))

    # we define our model: y = W*x + b
    y = tf.matmul(x, W) + b

    # MSE:
    cost = tf.reduce_sum(tf.pow(y - y_, 2)) / (2 * 1000)
    optimizer = tf.train.GradientDescentOptimizer(0.5).minimize(cost)

    # initialize variables to random values
    init = tf.global_variables_initializer()
    sess.run(init)
    # run optimizer on entire training data set many times
    for epoch in range(20000):
        sess.run(optimizer, feed_dict={x: train_ins, y_: train_outs.reshape(1, -1).T})
        # every 1000 iterations record progress
        if (epoch+1) % 1000 == 0:
            c = sess.run(cost, feed_dict={x: train_ins, y_: train_outs.reshape(1, -1).T})
            print("Epoch:", '%04d' % (epoch+1), "cost=", "{:.9f}".format(c))

    # train
    predict = y
    p = sess.run(predict, feed_dict={x: train_ins})
    position = 2 * ((p > 0) - .5)
    train_returns = position.reshape(-1) * train_outs
    # plot(np.cumprod(returns + 1))

    #test
    predict = y
    p = sess.run(predict, feed_dict={x: test_ins})
    position = 2*((p>0)-.5)
    test_returns = position.reshape(-1) * test_outs

    return train_returns, test_returns


def submit_buy_order(ticker, transaction_side, ttype, time_in_force):
    global api
    return api.submit_order(ticker, transaction_side, ttype, time_in_force)
