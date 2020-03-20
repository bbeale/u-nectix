#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.asset_selector import AssetSelector
from src.broker import BrokerException
from datetime import datetime, timedelta
from pytz import timezone
from finta import TA
import pandas as pd

# from util import time_from_datetime
# import statistics
# import time


def run(broker, args):

    if not broker or broker is None:
        raise BrokerException("[!] A broker instance is required.")
    else:
        broker = broker

    if args.period is None:
        args.period = "1D"
    if args.algorithm is None:
        args.algorithm = "bullish_macd_overnight_hold"
    if args.testperiods is None:
        args.testperiods = 30
    if args.max is None:
        args.max = 26
    if args.min is None:
        args.min = 6
    if args.poolsize is None:
        args.poolsize = 5

    if args.cash is not None and type(args.cash) == float:
        cash = args.cash
    else:
        cash = float(broker.cash)

    if args.risk_pct is not None and type(args.risk_pct) in [int, float]:
        risk_pct = args.risk_pct
    else:
        risk_pct = .10

    # initial trade state
    starting_amount = cash
    risk_amount = broker.calculate_tolerable_risk(cash, risk_pct)
    asset_selector = AssetSelector(broker, args, edgar_token=None)
    symbols = asset_selector.portfolio

    if args.backtest:
        # TODO: Make all time usages consistent
        now = datetime.now(timezone("EST"))
        beginning = now - timedelta(days=args.testperiods)
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

            # calculate MACD based ratings for a particular day
            ratings = get_ratings(symbols, broker, timezone('EST').localize(calendar.date), window_size=10)
            portfolio = portfolio_allocation(ratings, risk_amount)
            for _, row in ratings.iterrows():
                # "Buy" our shares on that day and subtract the cost.
                shares_to_buy = int(portfolio[row['symbol']])
                cost = round(round(row['price'], 2) * shares_to_buy, 2)
                cash -= cost

                # calculate the amount we want to risk on the next trade
                risk_amount = broker.calculate_tolerable_risk(cash, risk_pct)
            cal_index += 1
    else:
        # do stuff from the run live function
        pass

def get_ratings(symbols, broker, algo_time=None, window_size=5):
    """Calculate trade decision based on MACD values.

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

    ratings = pd.DataFrame(columns=['symbol', 'rating', 'close', 'macd', 'signal'])
    index = 0
    window_size = window_size
    formatted_time = None
    if algo_time is not None:
        formatted_time = algo_time.date().strftime('%Y-%m-%dT%H:%M:%S.%f-04:00')
    while index < len(symbols):
        barset = broker.api.get_barset(
            symbols=symbols,
            timeframe='day',
            limit=window_size,
            end=formatted_time
        )

        for symbol in symbols:
            bars = barset[symbol]
            if len(bars) == window_size:
                latest_bar = bars[-1].t.to_pydatetime().astimezone(
                    timezone('EST')
                )
                gap_from_present = algo_time - latest_bar
                if gap_from_present.days > 1:
                    continue

                price = bars[-1].c
                macd = TA.MACD(bars.df)
                current_macd = macd["MACD"].iloc[-1]
                current_signal = macd["SIGNAL"].iloc[-1]
                signal_divergence = current_macd - current_signal

                if signal_divergence < 0 and current_macd < 0:
                    ratings = ratings.append({
                        'symbol': symbol,
                        'rating': signal_divergence,
                        'close': price,
                        'macd': current_macd,
                        'signal': current_signal
                    }, ignore_index=True)
        index += 200
    ratings = ratings.sort_values('rating', ascending=False)
    return ratings.reset_index(drop=True)


def portfolio_allocation(data, cash):
    total_rating = data['rating'].sum()
    shares = {}
    for _, row in data.iterrows():
        shares[row['symbol']] = float(row['rating']) / float(total_rating) * float(cash) / float(row['close'])
    return shares
