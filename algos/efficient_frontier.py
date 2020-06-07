#!/usr/bin/env python
# -*- coding: utf-8 -*-
from algos import BaseAlgo
from src.asset_selector import AssetSelector, AssetValidationException, AssetException
from broker import BrokerException
from util import time_from_datetime
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import expected_returns
from pypfopt import risk_models
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import time

# import statistics
# from pypfopt.cla import CLA


class Algorithm(AssetSelector, BaseAlgo):

    def __init__(self, broker, cli_args):
        super().__init__(broker=broker, cli_args=cli_args, edgar_token=None)

    """ Custom asset selection method goes here."""
    def efficient_frontier(self, backtest=False, bt_offset=None):
        """
        Given a list of assets, evaluate which ones are bullish and return a sample of each.

        These method names should correspond with files in the algos/ directory.
        """
        if not self.poolsize or self.poolsize is None or self.poolsize is 0:
            raise AssetValidationException('[!] Invalid pool size.')

        self.portfolio = []
        if backtest:
            if not bt_offset or bt_offset is None:
                raise AssetValidationException('[!] Must specify a number of periods to offset if backtesting.')
            limit = bt_offset
        else:
            limit = 1000

        # guess these need to be in scope for the whole function
        start = None
        end = None

        while len(self.portfolio) < self.poolsize:
            for ass in self.tradeable_assets:
                """ The extraneous stuff that currently happens before the main part of evaluate_candlestick """
                if backtest:
                    # df = self.broker.get_asset_df(ass.symbol, self.period, start=time_from_datetime(self.backtest_beginning), end=time_from_datetime(self.beginning))
                    start = time_from_datetime(self.backtest_beginning)
                    end = time_from_datetime(self.beginning)
                else:
                    # df = self.broker.get_asset_df(ass.symbol, self.period, start=time_from_datetime(self.beginning), end=time_from_datetime(self.now))
                    start = time_from_datetime(self.beginning)
                    end = time_from_datetime(self.now)

                # get the dataframe
                df = self.broker.get_asset_df(ass.symbol, self.period, limit=limit, start=start, end=end)

                # guard clauses to make sure we have enough data to work with
                if df is None or df.empty:
                    continue

                # is the most recent date in the data frame the end date?
                df_end_date = str(df.iloc[-1].name).split(' ')[0]
                has_end_date = df_end_date in end
                if not has_end_date:
                    continue

                # throw it away if the price is out of our min-max range
                close = df['close'].iloc[-1]
                if close > self.max_stock_price or close < self.min_stock_price:
                    continue

                # throw it away if the candlestick pattern is not bullish
                # pattern = self.candle_pattern_direction(df)
                # if pattern in ['bear', None]:
                #     continue

                # assume the current symbol pattern is bullish and add to the portfolio
                self.portfolio.append(ass.symbol)
                if len(self.portfolio) >= self.poolsize:
                    # exit the filter process
                    break

        # haven't yet encountered a way where start and end get unset, but here's a guard clause just in case
        if start is None or end is None:
            raise AssetException('[!] Somehow start and end got unassigned')

        # EF calculation
        df = self.broker.api.get_barset(symbols=','.join(self.portfolio), limit=limit, timeframe=self.period, start=start, end=end)

        for k, v in df.items():
            df[k] = v.df['close']

        mean_return = expected_returns.mean_historical_return(df)
        sample_cov_matrix = risk_models.sample_cov(df)
        frontier = EfficientFrontier(mean_return, sample_cov_matrix)
        # reset instance portfolio to contents of frontier.tickers
        self.portfolio = frontier.tickers

    def get_ratings(self, algo_time=None, window_size=5):
        """Calculate trade decision based on standard deviation of past volumes.

        Per Medium article:
            Rating = Number of volume standard deviations * momentum.

        :param algo_time:
        :param window_size:
        :return:
        """
        if not algo_time or algo_time is None:
            raise ValueError('[!] Invalid algo_time.')

        ratings = pd.DataFrame(columns=['symbol', 'rating', 'price'])
        index = 0
        window_size = window_size
        formatted_time = None
        if algo_time is not None:
            # TODO: Consolidate these time usages
            formatted_time = algo_time.date().strftime('%Y-%m-%dT%H:%M:%S.%f-04:00')

        symbols = self.portfolio

        while index < len(symbols):
            barset = self.broker.api.get_barset(symbols=symbols, timeframe='day', limit=window_size, end=formatted_time)

            for symbol in symbols:
                bars = barset[symbol]
                if len(bars) == window_size:
                    # make sure we aren't missing the most recent data.
                    latest_bar = bars[-1].t.to_pydatetime().astimezone(timezone('EST'))
                    gap_from_present = algo_time - latest_bar
                    if gap_from_present.days > 1:
                        continue

                    price = bars[-1].c
                    price_change = price - bars[0].c

                    # # calculate standard deviation of previous volumes
                    # past_volumes = [bar.v for bar in bars[:-1]]
                    # volume_stdev = statistics.stdev(past_volumes)
                    # if volume_stdev == 0:
                    #     # data for the stock might be low quality.
                    #     continue
                    # # compare it to the change in volume since yesterday.
                    # volume_change = bars[-1].v - bars[-2].v
                    # volume_factor = volume_change / volume_stdev
                    # rating = price_change/bars[0].c * volume_factor

                    frontier_factor = 0
                    rating = 0
                    # TODO: efficient frontier rating calculation

                    if rating > 0:
                        ratings = ratings.append(
                            {'symbol': symbol, 'rating': price_change / bars[0].c * frontier_factor, 'price': price},
                            ignore_index=True)
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
            shares[row['symbol']] = float(row['rating']) / float(total_rating) * float(cash) / float(row['price'])
        # debug
        for k, v in shares.items():
            print('[*] Ticker: {}, Shares: {}'.format(k, v))
        return shares

    def total_asset_value(self, positions, date):
        """

        :param positions:
        :param date:
        :return:
        """
        if len(positions.keys()) == 0:
            return positions, 0,

        total_value = 0
        formatted_date = time_from_datetime(date)

        barset = self.broker.api.get_barset(symbols=positions.keys(), timeframe='day', limit=1, end=formatted_date)
        for symbol in positions:
            total_value += positions[symbol] * barset[symbol][0].o
        return positions, total_value,


def run(broker, args):

    if not broker or broker is None:
        raise BrokerException('[!] A broker instance is required.')
    else:
        broker = broker

    if args.period is None:
        args.period = '1D'
    if args.algorithm is None:
        args.algorithm = 'efficient_frontier'
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

    starting_amount = cash
    risk_amount = broker.calculate_tolerable_risk(cash, .10)
    algorithm = Algorithm(broker, args)

    symbols = algorithm.portfolio
    print('[*] Trading assets: {}'.format(','.join(symbols)))

    if args.backtest:
        # TODO: Make all time usages consistent
        now = datetime.now(timezone('EST'))
        beginning = now - timedelta(days=days_to_test)
        calendars = broker.get_calendar(start_date=beginning.strftime('%Y-%m-%d'), end_date=now.strftime('%Y-%m-%d'))
        portfolio = {}
        cal_index = 0

        for calendar in calendars:
            # see how much we got back by holding the last day's picks overnight
            positions, asset_value  = algorithm.total_asset_value(portfolio, calendar.date)
            cash += asset_value
            print('[*] Cash account value on {}: ${}'.format(calendar.date.strftime('%Y-%m-%d'), round(cash, 2)),
                'Risk amount: ${}'.format(round(risk_amount, 2)))

            if cal_index == len(calendars) - 1:
                print('[*] End of the backtesting window.')
                print('[*] Starting account value: {}'.format(starting_amount))
                print('[*] Holdings: ')
                for k, v in portfolio.items():
                    print(' - Symbol: {}, value: {}'.format(k, str(round(v, 2))))
                print('[*] Account value: {}'.format(round(cash, 2)))
                print('[*] Change from starting value: ${}'. format(round(float(cash) - float(starting_amount), 2)))
                break

            # calculate position size based on volume/momentum rating
            ratings = algorithm.get_ratings(timezone('EST').localize(calendar.date), window_size=10)
            portfolio = algorithm.portfolio_allocation(ratings, risk_amount)
            for _, row in ratings.iterrows():
                shares_to_buy = int(portfolio[row['symbol']])
                cost = row['price'] * shares_to_buy
                cash -= cost

                # calculate the amount we want to risk on the next trade
                risk_amount = broker.calculate_tolerable_risk(cash, .10)
            cal_index += 1
    else:
        cycle = 0
        bought_today = False
        sold_today = False
        try:
            orders = broker.get_orders(after=time_from_datetime(datetime.today() - timedelta(days=1)), limit=400, status='all')
        except BrokerException:
            # We don't have any orders, so we've obviously not done anything today.
            pass
        else:
            for order in orders:
                if order.side == 'buy':
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
                        print('[+] Buying position(s).')
                        portfolio_cash = float(broker.api.get_account().cash)
                        ratings = algorithm.get_ratings(window_size=10)
                        portfolio = algorithm.portfolio_allocation(ratings, portfolio_cash)
                        for symbol in portfolio:
                            broker.api.submit_order(symbol=symbol, qty=portfolio[symbol], side='buy', type='market',
                                time_in_force='day')
                        print('[*] Position(s) bought.')
                        bought_today = True
                else:
                    # sell our old positions before buying new ones.
                    time_after_open = clock.next_open - clock.timestamp
                    if time_after_open.seconds >= 60:
                        print('[-] Liquidating positions.')
                        broker.api.close_all_positions()
                    sold_today = True
            else:
                bought_today = False
                sold_today = False
                if cycle % 10 == 0:
                    print('[*] Waiting for next market day...')
            time.sleep(30)
            cycle += 1
