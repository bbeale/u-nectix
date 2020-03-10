#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import time_from_datetime
from src.asset_selector import AssetSelector
from src.broker import BrokerException
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import statistics
import time


def run(broker, args):

    if not broker or broker is None:
        raise BrokerException("[!] A broker instance is required.")
    else:
        broker = broker

    if args.testperiods is not None and type(args.testperiods) == int:
        days_to_test = args.testperiods
    else:
        days_to_test = 30

    # initial trade state
    cash            = float(broker.cash)
    risk_amount     = broker.calculate_tolerable_risk(cash, .10)
    stocks_to_hold  = None
    asset_selector  = AssetSelector(broker, args, edgar_token=None)

    """Trying to set up something similar to that in here
    https://medium.com/automation-generation/building-and-backtesting-a-stock-trading-script-in-python-for-beginners-105f8976b473

    If I can hack that together, maybe I can abstract enough for easy reuse between algos.
    
    Calling the contents of the algos folder by their selection method (bullish_candlestick) doesn't make sense in that regard since its not an actual algo
    
    """
    symbols = asset_selector.portfolio
    if args.backtest:
        # TODO: Make all time usages consistent
        now = datetime.now(timezone("EST"))
        beginning = now - timedelta(days=days_to_test)
        calendars = broker.get_calendar(start_date=beginning.strftime("%Y-%m-%d"), end_date=now.strftime("%Y-%m-%d"))
        shares = {}
        cal_index = 0
        for calendar in calendars:
            # see how much we got back by holding the last day's picks overnight
            cash += broker.calculate_total_asset_value(shares, calendar.date)
            print("[*] Cash account value on {}: ${}".format(calendar.date.strftime("%Y-%m-%d"), round(cash, 2)),
                "Risk amount: ${}".format(round(risk_amount, 2)))

            if cal_index == len(calendars) - 1:
                print("[*] End of the backtesting window.")
                break

            symbols = asset_selector.portfolio
            # Get the ratings for a particular day
            # TODO: Move ratings calculation into AssetSelector process
            # ratings = get_ratings(symbols, broker, stocks_to_hold, timezone('EST').localize(calendar.date), window_size=10)
            allocation = portfolio_allocation(symbols, risk_amount)
            for _, row in allocation:
                # "Buy" our shares on that day and subtract the cost.
                shares_to_buy = int(shares[row['symbol']])
                cost = round(round(row['price'], 2) * shares_to_buy, 2)
                cash -= cost
                cash = round(cash, 2)

                # calculate the amount we want to risk on the next trade
                risk_amount = broker.calculate_tolerable_risk(cash, .10)
            cal_index += 1
    else:
        # do stuff from the run live function
        pass

# def get_ratings(symbols, broker, shares_to_hold, algo_time, window_size=5):
#     """
#     TODO: validate these args
#
#     :param symbols:
#     :param broker:
#     :param shares_to_hold:
#     :param algo_time:
#     :param window_size:
#     :return:
#     """
#     ratings = pd.DataFrame(columns=['symbol', 'rating', 'price'])
#     index = 0
#     # The number of days of data to consider
#     window_size = window_size
#     formatted_time = None
#     if algo_time is not None:
#         # Convert the time to something compatable with the Alpaca API.
#         formatted_time = algo_time.date().strftime('%Y-%m-%dT%H:%M:%S.%f-04:00')
#     while index < len(symbols):
#         # Retrieve data for this batch of symbols.
#         barset = broker.api.get_barset(
#             symbols=symbols,
#             timeframe='day',
#             limit=window_size,
#             end=formatted_time
#         )
#
#         for symbol in symbols:
#             bars = barset[symbol]
#             if len(bars) == window_size:
#                 # Make sure we aren't missing the most recent data.
#                 latest_bar = bars[-1].t.to_pydatetime().astimezone(
#                     timezone('EST')
#                 )
#                 gap_from_present = algo_time - latest_bar
#                 if gap_from_present.days > 1:
#                     continue
#
#                 # Now, if the stock is within our target range, rate it.
#                 price = bars[-1].c
#                 # min max price check used to be here -- make sure it still works
#                 price_change = price - bars[0].c
#                 # Calculate standard deviation of previous volumes
#                 past_volumes = [bar.v for bar in bars[:-1]]
#                 volume_stdev = statistics.stdev(past_volumes)
#                 if volume_stdev == 0:
#                     # The data for the stock might be low quality.
#                     continue
#                 # Then, compare it to the change in volume since yesterday.
#                 volume_change = bars[-1].v - bars[-2].v
#                 volume_factor = volume_change / volume_stdev
#                 # Rating = Number of volume standard deviations * momentum.
#                 rating = price_change/bars[0].c * volume_factor
#                 if rating > 0:
#                     ratings = ratings.append({
#                         'symbol': symbol,
#                         'rating': price_change/bars[0].c * volume_factor,
#                         'price': price
#                     }, ignore_index=True)
#         index += 200
#     ratings = ratings.sort_values('rating', ascending=False)
#     ratings = ratings.reset_index(drop=True)
#     return ratings[:shares_to_hold]


def portfolio_allocation(data, cash):
    total_rating = data['rating'].sum()
    shares = {}
    for _, row in data.iterrows():
        shares[row['symbol']] = float(row['rating']) / float(total_rating) * float(cash) / float(row['price'])
    return shares
