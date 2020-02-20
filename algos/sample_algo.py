#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.indicator_collection import Indicators as Indicators
from src.asset_selector import AssetSelector
from src.broker import BrokerException
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import statistics

from util import time_formatter
import time


def run(broker, args):

    if not broker or broker is None:
        raise BrokerException("[!] A broker instance is required.")
    else:
        broker = broker

    if args.days is not None and type(args.days) == int:
        days_to_test = args.days
    else:
        days_to_test = 30

    # initial trade state
    trading_symbol  = None
    trading         = False
    cash            = broker.cash
    portfolio_amount = broker.buying_power
    max_stock_price = args.max
    min_stock_price = args.min
    stocks_to_hold  = 150
    # backdate        = time_formatter(time.time() - (604800 * 54))
    asset_selector  = AssetSelector(broker, args, edgar_token=None)
    # tickers         = asset_selector.bullish_candlesticks()
    indicators      = Indicators(broker, args, asset_selector).data

    """Trying to set up something similar to that in here
    https://medium.com/automation-generation/building-and-backtesting-a-stock-trading-script-in-python-for-beginners-105f8976b473

    If I can hack that together, maybe I can abstract enough for easy reuse between algos.
    
    Calling the contents of the algos folder by their selection method (bullish_candlestick) doesn't make sense in that regard since its not an actual algo
    
    """

    if args.backtest:
        # do stuff from the backtest function
        now = datetime.now(timezone('EST'))
        beginning = now - timedelta(days=days_to_test)

        # The calendars API will let us skip over market holidays and handle early
        # market closures during our backtesting window.
        calendars = broker.api.get_calendar(start=beginning.strftime("%Y-%m-%d"), end=now.strftime("%Y-%m-%d"))
        shares = {}
        cal_index = 0
        for calendar in calendars:
            # See how much we got back by holding the last day's picks overnight
            # portfolio_amount += get_value_of_assets(api, shares, calendar.date)
            print('Portfolio value on {}: ${:0.2f}'.format(calendar.date.strftime('%Y-%m-%d'), portfolio_amount))

            if cal_index == len(calendars) - 1:
                # We've reached the end of the backtesting window.
                break
            symbols = asset_selector.trading_assets
            # Get the ratings for a particular day
            ratings = get_ratings(symbols, broker, max_stock_price, min_stock_price, stocks_to_hold, timezone('EST').localize(calendar.date))
            shares = get_shares_to_buy(ratings, portfolio_amount)
            for _, row in ratings.iterrows():
                # "Buy" our shares on that day and subtract the cost.
                shares_to_buy = shares[row['symbol']]
                cost = row['price'] * shares_to_buy
                portfolio_amount -= cost
            cal_index += 1
    else:
        # do stuff from the run live function
        pass

def get_ratings(symbols, broker, max_price, min_price, shares_to_hold, algo_time):
    # assets = api.list_assets()
    # assets = [asset for asset in assets if asset.tradable ]
    ratings = pd.DataFrame(columns=['symbol', 'rating', 'price'])
    index = 0
    batch_size = 200 # The maximum number of stocks to request data for
    window_size = 5 # The number of days of data to consider
    formatted_time = None
    if algo_time is not None:
        # Convert the time to something compatable with the Alpaca API.
        formatted_time = algo_time.date().strftime('%Y-%m-%dT%H:%M:%S.%f-04:00')
    while index < len(symbols):
        # Retrieve data for this batch of symbols.
        barset = broker.api.get_barset(
            symbols=symbols,
            timeframe='day',
            limit=window_size,
            end=formatted_time
        )

        for symbol in symbols:
            bars = barset[symbol]
            if len(bars) == window_size:
                # Make sure we aren't missing the most recent data.
                latest_bar = bars[-1].t.to_pydatetime().astimezone(
                    timezone('EST')
                )
                gap_from_present = algo_time - latest_bar
                if gap_from_present.days > 1:
                    continue

                # Now, if the stock is within our target range, rate it.
                price = bars[-1].c
                if price <= max_price and price >= min_price:
                    price_change = price - bars[0].c
                    # Calculate standard deviation of previous volumes
                    past_volumes = [bar.v for bar in bars[:-1]]
                    volume_stdev = statistics.stdev(past_volumes)
                    if volume_stdev == 0:
                        # The data for the stock might be low quality.
                        continue
                    # Then, compare it to the change in volume since yesterday.
                    volume_change = bars[-1].v - bars[-2].v
                    volume_factor = volume_change / volume_stdev
                    # Rating = Number of volume standard deviations * momentum.
                    rating = price_change/bars[0].c * volume_factor
                    if rating > 0:
                        ratings = ratings.append({
                            'symbol': symbol,
                            'rating': price_change/bars[0].c * volume_factor,
                            'price': price
                        }, ignore_index=True)
        index += 200
    ratings = ratings.sort_values('rating', ascending=False)
    ratings = ratings.reset_index(drop=True)
    return ratings[:shares_to_hold]


def get_shares_to_buy(ratings_df, portfolio):
    total_rating = ratings_df['rating'].sum()
    shares = {}
    for _, row in ratings_df.iterrows():
        shares[row['symbol']] = int(
            row['rating'] / total_rating * portfolio / row['price']
        )
    return shares
