#!/usr/bin/env python
# -*- coding: utf-8 -*-
from broker import BrokerException, BrokerValidationException
from broker.broker import Broker
from broker.krak_dealer import KrakDealer
from broker.forex_broker import ForexBroker
from util import parse_configs, parse_args
from pykrakenapi.pykrakenapi import KrakenAPI, KrakenAPIError
from alpaca_trade_api.rest import REST, APIError
from v20.errors import V20ConnectionError
from importlib import import_module
import krakenex
import v20


def main(config, args):

    # are we trading forex?
    if args.forex:
        print('[-] do stuff with Oanda.')
        try:
            oanda = v20.Context(
                config['oanda']['host'],
                config['oanda']['port'],
                token=config['oanda']['token']
            )
        except V20ConnectionError as error:
            raise error

        pair = 'EUR_USD'

        try:
            broker = ForexBroker(oanda, pair)
        except BrokerException as error:
            raise error
        else:
            # is our account restricted from trading?
            if broker.trading_blocked:
                raise BrokerException('[!] Insufficient trading balances, or account is otherwise restricted from trading.')

        # how much money can we use to open new positions?
        if args.cash is not None:
            print('[?] ${} in simulated account balance.'.format(args.cash))
        else:
            print('[?] ${} is available in cash.'.format(broker.trade_balance['tb']))

    # are we trading crypto?
    if args.crypto:
        print('[-] do stuff with Kraken.')
        try:
            api = krakenex.API(key=config['kraken']['api_key'], secret=config['kraken']['private_key'])
            kraken = KrakenAPI(api, tier='Starter')
        except KrakenAPIError as error:
            raise error

        pair = 'BATUSD'

        try:
            broker = KrakDealer(kraken, pair=pair)
        except BrokerException as error:
            raise error
        else:
            # is our account restricted from trading?
            if broker.trading_blocked:
                raise BrokerException('[!] Insufficient trading balances, or account is otherwise restricted from trading.')

        # how much money can we use to open new positions?
        if args.cash is not None:
            print('[?] ${} in simulated account balance.'.format(args.cash))
        else:
            print('[?] ${} is available in cash.'.format(broker.trade_balance['tb']))

    else:
        # we must be trading stocks
        try:
            alpaca = REST(base_url=config['alpaca']['APCA_API_BASE_URL'], key_id=config['alpaca']['APCA_API_KEY_ID'],
                secret_key=config['alpaca']['APCA_API_SECRET_KEY'], api_version=config['alpaca']['VERSION'])
        except APIError as error:
            raise error

        try:
            broker = Broker(alpaca)
        except (BrokerException, BrokerValidationException, Exception) as error:
            raise error
        else:
            # is our account restricted from trading?
            if broker.trading_blocked:
                raise BrokerException('[!] Account is currently restricted from trading.')

        # how much money can we use to open new positions?
        if args.cash is not None:
            print('[?] ${} in simulated account balance.'.format(args.cash))
        else:
            print('[?] ${} is available in cash.'.format(broker.cash))

    # try and import the corresponding Python file from algos
    try:
        algorithm = import_module(f'algos.{args.algorithm}', package='Algorithm')
    except ImportError as error:
        raise error
    else:
        algorithm.run(broker, args)


if __name__ == '__main__':
    configuration = parse_configs()
    arguments = parse_args()
    main(configuration, arguments)
