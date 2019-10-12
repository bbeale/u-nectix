#!/usr/bin/env python
# -*- coding: utf-8 -*-
from alpaca_functions import (
    time_formatter,
    calculate_indicators_v2 as calculate_indicators,
    get_predictions,
    get_sentiment,
    bullish_candlestick_patterns,
    get_stuff_to_trade_v2,
    bullish_sequence,
    submit_buy_order
)
import numpy as np
import time
import os


def main():

    candlestickPatternStart = time_formatter(time.time() - 604800)

    today = time_formatter(time.time())
    start = time_formatter(time.time() - (604800 * 13))

    # get ticker to trade
    raw_data = get_stuff_to_trade_v2(candlestickPatternStart)

    securities = dict()

    for item in raw_data.keys():
        indicators = calculate_indicators(item, start)

        sentiment = get_sentiment(item)
        if sentiment == "positive":
            securities[item] = indicators

    for item in securities.items():
        if bullish_sequence(item[1]["macd"].iloc[-3], item[1]["macd"].iloc[-2], item[1]["macd"].iloc[-1]):
            if item[1]["macd"].iloc[-1] >= item[1]["signal"].iloc[-1]:
                print("buy!")
                submit_buy_order(item[0], "buy", "market", "ioc")

    print(".")


if __name__ == "__main__":
    main()
