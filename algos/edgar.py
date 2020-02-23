#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.indicator_collection import Indicators as Indicators
from src.edgar_interface import EdgarInterface
from src.asset_selector import AssetSelector
from src.broker import BrokerException
from util import time_formatter, submit_order
from src.sentiment_analysis import SentimentAnalysis as Sent
from src.twitter_interface import TwitterInterface
from src.predictor import Predictor
import time

def run(broker, args, edgar_token):

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
    # backdate        = time_formatter(time.time() - (604800 * 54))
    asset_selector  = AssetSelector(broker, args, edgar_token=None)
    # tickers         = asset_selector.bullish_candlesticks()
    indicators      = Indicators(broker, args, asset_selector).data
    edgar           = EdgarInterface(edgar_token, indicators).get_edgar_signals()

    # TODO: SEC form sentiment analysis
    # tweets          = TwitterInterface(twitter_api, indicators).get_ticker_tweets()
    # sentiments      = Sent(indicators, tweets).get_sentiments()
    # predictions     = Predictor(indicators).get_securities_predictions()

    # trade decision here
    for e in edgar.keys():

        instrument = indicators[e]
        # check the most recent moving average convergence-divergence
        # has the MACD crossed over its signal and is the MACD percentage change is positive?
        if instrument["macd"].iloc[-1] > instrument["signal"].iloc[-1] and instrument["macd_ptc"].iloc[-1] > 0:
            # if the MACD checks out, check the directional movement indicator
            # has the DMI positive value crossed over the negative value?
            if instrument["DMp"].iloc[-1] > instrument["DMm"].iloc[-1]:
                # if the DMI checks out, what is the EDGAR signal?
                if e["signal"] in ["BULL", "STRONGBULL"]:
                    trading = True
                    trading_symbol = str(e)
            else:
                # if DMI has not crossed over, check for a stronger EDGAR signal
                if e["signal"] is "STRONGBULL":
                    trading = True
                    trading_symbol = str(e)

        if trading_symbol is not None:
            break

    if trading is True:
        # decide how much to buy # TODO
        quant = 10

        # then submit a buy order
        submit_order(
            api_reference=broker.alpaca_api,
            ticker=trading_symbol,
            qty=quant,
            transaction_side="buy",
            ttype="market",
            time_in_force="ioc"
        )
