#!/usr/bin/env python
# -*- coding: utf-8 -*-
from alpaca_functions import time_formatter, calculate_indicators, get_predictions, get_sentiment
import time
import os


def main():

    today = time_formatter(time.time())
    start = time_formatter(time.time() - (604800 * 13))         # Trying with the last 120 ish days # 52))

    # raw_data, ticker = get_stuff_to_trade(today, start)

    ticker = "AMAT"
    raw_data = os.path.relpath("data/AMAT_test_data_1D_year_OCT2018-2019_2.csv")        # 1d window

    # Calculate indicators and stuff
    indicators = calculate_indicators(raw_data, ticker)
    indicators = get_sentiment(ticker, indicators)
    # get_edgar_score(indicators, ticker)

    # Train models
    print("closing price")
    close_train, close_test = get_predictions(indicators["data"]["close"])
    print("macd")
    macd_train, macd_test = get_predictions(indicators["macd"])
    signal_train, signal_test = get_predictions(indicators["signal"])
    print("MFI")
    mfi_train, mfi_test = get_predictions(indicators["mfi"])
    print("Stochastic oscillator")
    stoch_train, stoch_test = get_predictions(indicators["stoch"])

    print(".")


if __name__ == "__main__":
    main()
