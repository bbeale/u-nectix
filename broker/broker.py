#!/usr/bin/env python
# -*- coding: utf-8 -*-
from broker import BrokerException, BrokerValidationException
import pandas as pd


class Broker(object):

    def __init__(self, api):

        if not api or api is None:
            raise BrokerValidationException('[!] API instance required.')

        self.api = api
        self.trading_account = self.get_account()
        self.cash = self.trading_account.cash
        self.buying_power = self.trading_account.buying_power
        self.original_cash = self.cash
        self.original_buying_power = self.buying_power
        self.trading_blocked = self.trading_account.trading_blocked
        self.clock = self.get_clock()

    def _update_position_data(self, ticker: str, timestamp, price: float):
        raise NotImplementedError

    def report(self):
        raise NotImplementedError

    """Data grabbing methods"""
    def get_account(self):
        try:
            result = self.api.get_account()
        except BrokerException as err:
            print('[!] Unable to get account.')
            raise err
        else:
            return result

    def get_clock(self):
        """Get the API clock object.

        :return:
        """
        try:
            return self.api.get_clock()
        except BrokerException as err:
            print('[!] Unable to get the clock.')
            raise err

    def get_calendar(self, start_date, end_date):
        """
        Requests Dates data from Alpaca and returns it as a list of Calendar objects.
        """
        if not start_date or start_date is None:
            raise BrokerValidationException('[!] Invalid start_date.')

        if not end_date or end_date is None:
            raise BrokerValidationException('[!] Invalid end_date.')

        try:
            result = self.api.get_calendar(start_date, end_date)
        except BrokerException as err:
            print('[!] Unable to get calendar.')
            raise err
        else:
            return result

    def get_assets(self):
        """Get assets from Alpaca API.

        :return:
        """
        try:
            result = self.api.list_assets(status='active')
        except BrokerException as err:
            print('[!] Unable to get assets.')
            raise err
        else:
            return result

    def get_asset(self, symbol):
        """Get an asset by ticker symbol from the Alpaca API.

        :return:
        """
        if not symbol or symbol is None:
            raise BrokerValidationException('[!] Invalid symbol.')

        try:
            result = self.api.get_asset(symbol=symbol)
        except BrokerException as err:
            print('[!] Unable to get asset.')
            raise err
        else:
            return result

    def get_positions(self):
        """Get a list of open positions for a given account.

        :return:
        """
        try:
            result = self.api.list_positions()
        except BrokerException as err:
            print('[!] Unable to get open positions.')
            raise err
        else:
            return result

    def get_position(self, symbol):
        """Get any open positions for a given symbol.

        :param symbol:
        :return:
        """
        if not symbol or symbol is None:
            raise BrokerValidationException('[!] Invalid symbol.')

        try:
            result = self.api.get_position(symbol)
        except BrokerException as err:
            print(f'[!] Unable to get postion or positions for {symbol}.')
            raise err
        else:
            return result

    def close_all_positions(self):
        """Liquidate all positions. API returns 500 error (wtf?) when posiiotn cannot be closed.

        :return:
        """
        try:
            result = self.api.close_all_positions()
        except BrokerException as err:
            print('[!] An error occurred when liquidating posiitons.')
            raise err
        else:
            return result

    def close_position(self, symbol):
        """Close position for a given symbol.

        :return:
        """
        if not symbol or symbol is None:
            raise BrokerValidationException('[!] Invalid symbol.')

        try:
            result = self.api.close_position(symbol)
        except BrokerException as err:
            print(f'[!] An error occurred when closing {symbol} posiitons.')
            raise err
        else:
            return result

    def get_orders(self, status='open', limit=50, after=None, until=None, direction='desc'):
        """Get a list of orders for a given accountt.

        :param status: 'open', 'closed', or 'all'. API defaults to open, so does this
        :param limit: API default is 50, with a limit of 500
        :param after: Include only pos
        :param until:
         :param direction:
        :return:
        """
        try:
            result = self.api.list_orders(status=status, limit=limit, after=after, until=until, direction=direction)
        except BrokerException as err:
            print(f'[!] Unable to get {status} orders.')
            raise err
        else:
            return result

    def get_order(self, order_id, client_order_id=None):
        """Get an order for the given order_id.

        :param order_id:
        :param client_order_id:
        :return:
        """
        if client_order_id is not None:
            try:
                print('[+] Getting order by client_order_id.')
                result = self.api.get_order_by_client_order_id(client_order_id)
            except BrokerException as err:
                print(f'[!] Unable to get order for client_order_id {client_order_id}.')
                raise err
        else:
            if not order_id or order_id is None:
                raise BrokerValidationException('[!] Invalid order_id.')
            try:
                print('[+] Getting order the normal way by order_id.')
                result = self.api.get_order(order_id)
            except BrokerException as err:
                print('[!] Unable to get order {}.'.format(order_id))
                raise err
        return result

    def submit_order(self,
                     symbol,
                     quantity,
                     transaction_side,
                     transaction_type,
                     time_in_force,
                     limit_price=None,
                     stop_price=None,
                     extended_hours=False,
                     client_order_id=None):
        """Submit an order using a reference to the Alpaca API.

        :param symbol: Ticker symbol to trade
        :param quantity: Number of shares to trade
        :param transaction_side: Buy or sell
        :param transaction_type: Order type (market, limit, stop, or stop_limit)
        :param time_in_force: day, gtc, opg, cls, ioc, or fok
        :param limit_price:
        :param stop_price:
        :param extended_hours:
        :param client_order_id:
        :return:
        """
        if not symbol or symbol is None:
            raise BrokerValidationException('[!] Invalid ticker symbol.')

        if not quantity or quantity is None or len(quantity) < 1:
            raise BrokerValidationException('[!] Invalid qty.')

        if not transaction_side or transaction_side not in ['buy', 'sell']:
            raise BrokerValidationException('[!] Invalid transaction_side.')

        if not transaction_type or transaction_type not in ['market', 'limit', 'stop', 'stop_limit']:
            raise BrokerValidationException('[!] Invalid ttype.')

        if not time_in_force or time_in_force not in ['day', 'gtc', 'opg', 'cls', 'ioc', 'fok']:
            raise BrokerValidationException('[!] Invalid time_in_force.')

        # validate stop_price and limit_price if need be
        if transaction_type in ['limit', 'stop_limit'] and (not limit_price or limit_price is None):
            raise BrokerValidationException('[!] limit_price required if transaction_type is limit or stop_limit.')

        if transaction_type in ['stop', 'stop_limit'] and (not stop_price or stop_price is None):
            raise BrokerValidationException('[!] stop_price required if transaction_type is stop or stop_limit.')

        try:
            result = self.api.submit_order(
                symbol,
                quantity,
                transaction_side,
                transaction_type,
                time_in_force,
                limit_price,
                stop_price,
                # extended_hours,
                client_order_id)
        except BrokerException as err:
            print(f'[!] Unable to submit {transaction_side} order for {symbol}.')
            raise err
        else:
            return result

    def replace_order(self,
                     order_id,
                     quantity=None,
                     time_in_force=None,
                     limit_price=None,
                     stop_price=None,
                     client_order_id=None):
        """Submit an order using a reference to the Alpaca API.

        :param order_id: Ticker symbol to trade
        :param quantity: Number of shares to trade
        :param time_in_force: day, gtc, opg, cls, ioc, or fok
        :param limit_price:
        :param stop_price:
        :param client_order_id:
        :return:
        """
        if not order_id or order_id is None:
            raise BrokerValidationException('[!] Invalid ticker symbol.')

        try:
            # get an order so we can grab iuts type
            transaction_type = self.get_order(order_id)
        except BrokerException as err:
            raise BrokerValidationException('[!] A transaction_type is needed from the order object to validate stop and limit price parameters.')

        if not quantity or quantity is None or len(quantity) < 1:
            raise BrokerValidationException('[!] Invalid qty.')

        # validate stop_price and limit_price if need be
        if transaction_type in ['limit', 'stop_limit'] and (not limit_price or limit_price is None):
            raise BrokerValidationException('[!] limit_price required if transaction_type is limit or stop_limit.')

        if transaction_type in ['stop', 'stop_limit'] and (not stop_price or stop_price is None):
            raise BrokerValidationException('[!] stop_price required if transaction_type is stop or stop_limit.')

        try:
            result = self.api.replace_order(order_id, quantity, transaction_type, time_in_force, limit_price, stop_price, client_order_id)
        except BrokerException as err:
            print('[!] Unable to replace order.')
            raise err
        else:
            return result

    def cancel_all_orders(self):
        """Try to close all orders. API returns 500 error (wtf?) when posiiotn cannot be closed.

        :return:
        """
        try:
            result = self.api.cancel_all_orders()
        except BrokerException as err:
            print('[!] An error occurred when canceling orders.')
            raise err
        else:
            return result

    def cancel_order(self, order_id):
        """Cancel order for a given order_id.

        :return:
        """
        if not order_id or order_id is None:
            raise BrokerValidationException('[!] Invalid symbol.')

        try:
            result = self.api.close_position(order_id)
        except BrokerException as err:
            print(f'[!] An error occurred when canceling order {order_id}.')
            raise err
        else:
            return result

    def get_asset_df(self,
                     symbol,
                     period,
                     limit=1000,
                     start=None,
                     end=None):
        """Get a set of bars from the API given a symbol, a time period and a starting time.

        :param symbol:
        :param period:
        :param limit:
        :param start:
        :param end:
        :return:
        """
        if not symbol or symbol is None:
            raise BrokerValidationException('[!] Invalid symbol.')

        if not period or period is None:
            raise BrokerValidationException('[!] Must present a valid period type.')

        if start is None or end is None:
            raise BrokerValidationException('[!] Must present start and end dates.')

        try:
            result = self.api.get_barset(symbol, period, limit=limit, start=start, end=end)
        except BrokerException as err:
            print(f'[!] Unable to get barset for {symbol}.')
            raise err
        else:
            return self._bar_df(result[symbol])

    def get_watchlists(self):
        """Get all watchlists from the Alpaca API.

        These will be how we separate our buckets of assets based on intended trading strategy.

        :return:
        """
        try:
            result = self.api.get_watchlists()
        except BrokerException as err:
            print('[!] Unable to get watchlists.')
            raise err
        else:
            return result

    def get_watchlist(self, watchlist_id):
        """Get a list of items in a watchlist by watchlist_id, from the Alpaca API.

        :param watchlist_id:
        :return:
        """
        if not watchlist_id or watchlist_id is None:
            raise BrokerValidationException('[!] Invalid watchlist_id.')

        try:
            result = self.api.get_watchlist(watchlist_id=watchlist_id)
        except BrokerException as err:
            print(f'[!] Unable to get watchlist {watchlist_id}.')
            raise err
        else:
            return result

    def add_watchlist(self, watchlist_name):
        """Add a new watchlist.

        :param watchlist_name:
        :return:
        """
        if not watchlist_name or watchlist_name is None or watchlist_name is '':
            raise BrokerValidationException('[!] Invalid watchlist_name.')

        try:
            result = self.api.add_watchlist(watchlist_name=watchlist_name)
        except BrokerException as err:
            print(f'[!] Unable to add watchlist {watchlist_name}.')
            raise err
        else:
            return result

    def add_to_watchlist(self, watchlist_id, symbol):
        """Add a symbol to a watchlist.

        :param watchlist_id:
        :param symbol:
        :return:
        """
        if not watchlist_id or watchlist_id is None:
            raise BrokerValidationException('[!] Invalid watchlist_id.')

        if not symbol or symbol is None:
            raise BrokerValidationException('[!] Invalid symbol.')

        try:
            result = self.api.add_to_watchlist(watchlist_id=watchlist_id, symbol=symbol)
        except BrokerException as err:
            print(f'[!] Unable to add {symbol} to watchlist.')
            raise err
        else:
            return result

    def clear_watchlist(self, watchlist_id):
        """Remove all items in the assets collection of a given watchlist_id.

        :param watchlist_id: ID of the watchlist containing the assets we want to purge
        :return:
        """
        if not watchlist_id or watchlist_id is None:
            raise BrokerValidationException('[!] Invalid watchlist_id.')

        try:
            result = self.get_watchlist(watchlist_id)
        except BrokerException as err:
            print(f'[!] Unable to get watchlist {watchlist_id}.')
            raise err
        else:
            if len(result.assets) < 1:
                # return the watchlist right away if it's empty
                return result
            # let's try looping through and deleting one by one
            for ass in result.assets:
                try:
                    self.api.delete_from_watchlist(watchlist_id, ass['symbol'])
                except BrokerException as err:
                    print('[!] Unable to remove this item from the watchlist.')
                    raise err
                else:
                    # explicitly continuing to the next asset if no exceptions are thrown
                    continue
            # finally, grab the watchlist again now that it should be empty
            result = self.get_watchlist(watchlist_id)
            return result

    @staticmethod
    def _bar_df(bars):
        """Given a collection of candlestick bars, return a dataframe.
        Dataframe should contain keys:
            - time, open, high, low, close, volume
        :param bars:
        :return:
        """
        if bars is None or bars.df.empty:
            raise BrokerValidationException('[!] Bars cannot be none')

        data            = pd.DataFrame(index=[bar.t for bar in bars if bar is not None])
        data['open']    = [bar.o for bar in bars if bar is not None]
        data['high']    = [bar.h for bar in bars if bar is not None]
        data['low']     = [bar.l for bar in bars if bar is not None]
        data['close']   = [bar.c for bar in bars if bar is not None]
        data['volume']  = [bar.v for bar in bars if bar is not None]

        return data

    @staticmethod
    def calculate_tolerable_risk(balance, risk_pct):
        """Calculate the risk dollar amount of a balance given a percentage.

        :param balance:
        :param risk_pct:
        :return:
        """
        if not balance or balance is None or balance == 0:
            raise ValueError('[!] valid balance is required.')

        if not risk_pct or risk_pct is None or risk_pct == 0:
            raise ValueError('[!] risk_pct cannot be zero.')

        return float(balance) * float(risk_pct)

    @staticmethod
    def calculate_position_size(price, trading_balance, risk_pct=.10):
        """Given a stock price, available traselfding balance, and a risk percentage, calculate a position size for a trade.

        :param price:
        :param trading_balance:
        :param risk_pct:
        :return:
        """

        if not price or price is None:
            raise ValueError('[!] A price is required for this calculation.')

        if not trading_balance or trading_balance is None:
            raise ValueError('[!] A trading_balance is required for this calculation.')

        if risk_pct == 0:
            raise ValueError('[!] risk_pct cannot be zero.')

        return int(trading_balance * risk_pct / price)
