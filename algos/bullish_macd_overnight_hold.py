#!/usr/bin/env python
# -*- coding: utf-8 -*-
from algos import BaseAlgo
from src.asset_selector import AssetSelector, AssetValidationException
from src.broker import BrokerException
from util import time_from_datetime
from datetime import datetime, timedelta
from pytz import timezone
from finta import TA
import pandas as pd


class Algorithm(AssetSelector, BaseAlgo):

    def __init__(self, broker, cli_args):
        super().__init__(broker=broker, cli_args=cli_args, edgar_token=None)

    """ Custom asset selection method goes here."""
    def bullish_macd_overnight_hold(self):
        """
        Given a list of assets, evaluate which ones are bullish and return a sample of each.

        These method names should correspond with files in the algos/ directory.
        """
        if not self.poolsize or self.poolsize is None or self.poolsize is 0:
            raise AssetValidationException("[!] Invalid pool size.")

        self.portfolio = []

        for ass in self.tradeable_assets:
            """ The extraneous stuff that currently happens before the main part of evaluate_candlestick """
            limit = 1000
            df = self.broker.get_barset_df(ass.symbol, self.period, limit=limit)

            # guard clauses to make sure we have enough data to work with
            if df is None or len(df) != limit:
                continue

            # throw it away if the price is out of our min-max range
            close = df["close"].iloc[-1]
            if close > self.max_stock_price or close < self.min_stock_price:
                continue

            # Look for buy signals
            macd_signal = self.signaler.macd_signal.buy(df)
            mfi_signal = self.signaler.mfi_signal.buy(df)
            if macd_signal and mfi_signal:
                # add the current symbol to the portfolio
                self.portfolio.append(ass.symbol)
                if len(self.portfolio) >= self.poolsize:
                    # exit the filter process
                    break

    def get_ratings(self, algo_time=None, window_size=5):
        """Calculate trade decision based on MACD values.

        :param algo_time:
        :param window_size:
        :return:
        """
        if not algo_time or algo_time is None:
            raise ValueError("[!] Invalid algo_time.")

        ratings = pd.DataFrame(columns=['symbol', 'rating', 'close', 'macd', 'signal'])
        index = 0
        window_size = window_size
        formatted_time = None
        if algo_time is not None:
            formatted_time = algo_time.date().strftime('%Y-%m-%dT%H:%M:%S.%f-04:00')

        symbols = self.portfolio

        while index < len(symbols):
            barset = self.broker.api.get_barset(symbols=symbols, timeframe='day', limit=window_size, end=formatted_time)

            for symbol in symbols:
                bars = barset[symbol]
                if len(bars) == window_size:
                    latest_bar = bars[-1].t.to_pydatetime().astimezone(timezone('EST'))
                    gap_from_present = algo_time - latest_bar
                    if gap_from_present.days > 1:
                        continue

                    price = bars[-1].c
                    macd = TA.MACD(bars.df)
                    current_macd = macd["MACD"].iloc[-1]
                    current_signal = macd["SIGNAL"].iloc[-1]
                    signal_divergence = current_macd - current_signal

                    if signal_divergence < 0 and current_macd < 0:
                        ratings = ratings.append(
                            {'symbol': symbol, 'rating': signal_divergence, 'close': price, 'macd': current_macd,
                                'signal': current_signal}, ignore_index=True)
            index += 200
        ratings = ratings.sort_values('rating', ascending=False)
        return ratings.reset_index(drop=True)

    def portfolio_allocation(self, data, cash):
        """Calculate portfolio allocation size given a ratings dataframe and a cash amount.

        :param data:
        :param cash:
        :return:
        """
        total_rating = data['rating'].sum()
        shares = {}
        for _, row in data.iterrows():
            shares[row['symbol']] = int(float(row['rating']) / float(total_rating) * float(cash) / float(row['close']))
        # debug
        for k, v in shares.items():
            print("[*] Ticker: {}, Shares: {}".format(k, v))
        return shares


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
    algorithm = Algorithm(broker, args)

    symbols = algorithm.portfolio
    print("[*] Trading assets: {}".format(",".join(symbols)))

    if args.backtest:
        # TODO: Make all time usages consistent
        now = datetime.now(timezone("EST"))
        beginning = now - timedelta(days=args.testperiods)
        calendars = broker.get_calendar(start_date=beginning.strftime("%Y-%m-%d"), end_date=now.strftime("%Y-%m-%d"))
        portfolio = {}
        cal_index = 0

        for calendar in calendars:
            # see how much we got back by holding the last day's picks overnight
            asset_value = broker.calculate_total_asset_value(portfolio, calendar.date)
            cash += asset_value
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
            ratings = algorithm.get_ratings(timezone('EST').localize(calendar.date), window_size=10)
            portfolio = algorithm.portfolio_allocation(ratings, risk_amount)

            for _, row in ratings.iterrows():
                # "Buy" our shares on that day and subtract the cost.
                shares_to_buy = int(portfolio[row['symbol']])
                cost = row['close'] * shares_to_buy
                cash -= cost

                # calculate the amount we want to risk on the next trade
                risk_amount = broker.calculate_tolerable_risk(cash, risk_pct)
            cal_index += 1
    else:
        cycle = 0
        bought_today = False
        sold_today = False
        try:
            orders = broker.get_orders(after=time_from_datetime(datetime.today() - timedelta(days=1)), limit=400,
                status="all")
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
            pass
            # wait until the market's open to do anything.
            # clock = broker.get_clock()
            # if clock.is_open and not bought_today:
            #     if sold_today:
            #         time_until_close = clock.next_close - clock.timestamp
            #         if time_until_close.seconds <= 120:
            #             print("[+] Buying position(s).")
            #             portfolio_cash = float(broker.api.get_account().cash)
            #             ratings = algorithm.get_ratings(window_size=10)
            #             portfolio = algorithm.portfolio_allocation(ratings, portfolio_cash)
            #             for symbol in portfolio:
            #                 broker.api.submit_order(symbol=symbol, qty=portfolio[symbol], side="buy", type="market",
            #                     time_in_force="day")
            #             print("[*] Position(s) bought.")
            #             bought_today = True
            #     else:
            #         # sell our old positions before buying new ones.
            #         time_after_open = clock.next_open - clock.timestamp
            #         if time_after_open.seconds >= 60:
            #             print("[-] Liquidating positions.")
            #             broker.api.close_all_positions()
            #         sold_today = True
            # else:
            #     bought_today = False
            #     sold_today = False
            #     if cycle % 10 == 0:
            #         print("[*] Waiting for next market day...")
            # time.sleep(30)
            # cycle += 1
