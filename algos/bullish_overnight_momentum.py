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

    if args.period is None:
        args.period = "1D"
    if args.algorithm is None:
        args.algorithm = "bullish_overnight_momentum"
    if args.testperiods is None:
        args.testperiods = 30
    if args.max is None:
        args.max = 26
    if args.min is None:
        args.min = 6
    if args.poolsize is None:
        args.poolsize = 5

    if args.testperiods is not None and type(args.testperiods) == int:
        days_to_test = args.testperiods
    else:
        days_to_test = 30

    # initial trade state
    if args.cash is not None and type(args.cash) == float:
        cash = args.cash
    else:
        cash = float(broker.cash)

    if args.risk_pct is not None and type(args.risk_pct) in [int, float]:
        risk_pct = args.risk_pct
    else:
        risk_pct = .10
    starting_amount = cash
    risk_amount = broker.calculate_tolerable_risk(cash, risk_pct)
    stocks_to_hold = None
    asset_selector = AssetSelector(broker, args, edgar_token=None)

    """Trying to set up something similar to that in here
    https://medium.com/automation-generation/building-and-backtesting-a-stock-trading-script-in-python-for-beginners-105f8976b473

    If I can hack that together, maybe I can abstract enough for easy reuse between algos.
    
    Calling the contents of the algos folder by their selection method (bullish_candlestick) doesn't make sense in that regard since its not an actual algo
    
    """
    symbols = asset_selector.portfolio
    print("[*] Trading assets: {}".format(",".join(symbols)))
    if args.backtest:
        # TODO: Make all time usages consistent
        now = datetime.now(timezone("EST"))
        beginning = now - timedelta(days=days_to_test)
        calendars = broker.get_calendar(start_date=beginning.strftime("%Y-%m-%d"), end_date=now.strftime("%Y-%m-%d"))
        portfolio = {}
        cal_index = 0
        for calendar in calendars:
            # see how much we got back by holding the last day's picks overnight
            cash += broker.calculate_total_asset_value(portfolio, calendar.date)
            print("[*] Cash account value on {}: ${}".format(calendar.date.strftime("%Y-%m-%d"), round(cash, 2)),
                "Risk amount: ${}".format(round(risk_amount, 2)))

            if cal_index == len(calendars) - 1:
                print("[*] End of the backtesting window.")
                print("[*] Starting account value: {}".format(starting_amount))
                print("[*] Holdings: ")
                for k, v in portfolio.items():
                    print(" - Symbol: {}, Shares: {}".format(k, str(round(v, 2))))
                print("[*] Account value: {}".format(round(cash, 2)))
                print("[*] Change from starting value: ${}". format(round(float(cash) - float(starting_amount), 2)))
                break

            # calculate position size based on volume/momentum rating
            ratings = volume_momentum_ratings(symbols, broker, timezone("EST").localize(calendar.date), window_size=10)
            portfolio = portfolio_allocation(ratings, risk_amount)
            for _, row in ratings.iterrows():
                shares_to_buy = int(portfolio[row["symbol"]])
                cost = row["price"] * shares_to_buy
                cash -= cost

                # calculate the amount we want to risk on the next trade
                risk_amount = broker.calculate_tolerable_risk(cash, risk_pct)
            cal_index += 1
    else:
        cycle = 0
        bought_today = False
        sold_today = False
        try:
            orders = broker.get_orders(after=time_from_datetime(datetime.today() - timedelta(days=1)), limit=400, status="all")
        except BrokerException:
            # We don't have any orders, so we've obviously not done anything today.
            pass
        else:
            for order in orders:
                if order.side == "buy":
                    bought_today = True
                    # This handles an edge case where the script is restarted right before the market closes.
                    sold_today = True
                    break
                else:
                    sold_today = True

        while True:
            # wait until the market's open to do anything.
            clock = broker.get_clock()
            if clock.is_open and not bought_today:
                if sold_today:
                    time_until_close = clock.next_close - clock.timestamp
                    if time_until_close.seconds <= 120:
                        print("[+] Buying position(s).")
                        portfolio_cash = float(broker.api.get_account().cash)
                        ratings = volume_momentum_ratings(symbols, broker, stocks_to_hold, window_size=10)
                        portfolio = portfolio_allocation(ratings, portfolio_cash)
                        for symbol in portfolio:
                            broker.api.submit_order(symbol=symbol, qty=portfolio[symbol], side="buy", type="market",
                                time_in_force="day")
                        print("[*] Position(s) bought.")
                        bought_today = True
                else:
                    # sell our old positions before buying new ones.
                    time_after_open = clock.next_open - clock.timestamp
                    if time_after_open.seconds >= 60:
                        print("[-] Liquidating positions.")
                        broker.api.close_all_positions()
                    sold_today = True
            else:
                bought_today = False
                sold_today = False
                if cycle % 10 == 0:
                    print("[*] Waiting for next market day...")
            time.sleep(30)
            cycle += 1


def volume_momentum_ratings(symbols, broker, algo_time=None, window_size=5):
    """Calculate trade decision based on standard deviation of past volumes.

    Per Medium article:
        Rating = Number of volume standard deviations * momentum.

    :param symbols:
    :param broker:
    :param algo_time:
    :param window_size:
    :return:
    """
    if not symbols or symbols is None:
        raise ValueError('[!] Ticker symbols required for calculation.')

    if broker is None:
        raise ValueError("[!] Broker instance required.")

    if not algo_time or algo_time is None:
        raise ValueError("[!] Invalid algo_time.")

    ratings = pd.DataFrame(columns=["symbol", "rating", "price"])
    index = 0
    window_size = window_size
    formatted_time = None
    if algo_time is not None:
        # TODO: Consolidate these time usages
        formatted_time = algo_time.date().strftime("%Y-%m-%dT%H:%M:%S.%f-04:00")
    while index < len(symbols):
        barset = broker.api.get_barset(
            symbols=symbols,
            timeframe="day",
            limit=window_size,
            end=formatted_time
        )

        for symbol in symbols:
            bars = barset[symbol]
            if len(bars) == window_size:
                # make sure we aren"t missing the most recent data.
                latest_bar = bars[-1].t.to_pydatetime().astimezone(
                    timezone("EST")
                )
                gap_from_present = algo_time - latest_bar
                if gap_from_present.days > 1:
                    continue

                price = bars[-1].c
                price_change = price - bars[0].c
                # calculate standard deviation of previous volumes
                past_volumes = [bar.v for bar in bars[:-1]]
                volume_stdev = statistics.stdev(past_volumes)
                if volume_stdev == 0:
                    # data for the stock might be low quality.
                    continue
                # compare it to the change in volume since yesterday.
                volume_change = bars[-1].v - bars[-2].v
                volume_factor = volume_change / volume_stdev
                rating = price_change/bars[0].c * volume_factor
                if rating > 0:
                    ratings = ratings.append({
                        "symbol": symbol,
                        "rating": price_change/bars[0].c * volume_factor,
                        "price": price
                    }, ignore_index=True)
        index += 200
    ratings = ratings.sort_values("rating", ascending=False)
    return ratings.reset_index(drop=True)


def portfolio_allocation(data, cash):
    """Calculate portfolio allocation size given a ratings dataframe and a cash amount.

    :param data:
    :param cash:
    :return:
    """
    total_rating = data["rating"].sum()
    shares = {}
    for _, row in data.iterrows():
        num_shares = int(float(row["rating"]) / float(total_rating) * float(cash) / float(row["price"]))
        shares[row["symbol"]] = num_shares
    return shares
