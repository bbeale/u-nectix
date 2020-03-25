#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.indicator_collection import Indicators as Indicators
from src.edgar_interface import EdgarInterface
from src.asset_selector import AssetSelector
from src.broker import BrokerException
from algos import BaseAlgo
from util import time_from_timestamp
from src.sentiment_analysis import SentimentAnalysis as Sent
from src.twitter_interface import TwitterInterface
from src.predictor import Predictor
import time


class Algorithm(AssetSelector, BaseAlgo):

    def __init__(self, broker, cli_args):
        super().__init__(broker=broker, cli_args=cli_args, edgar_token=None)

    """ Interacting with the EDGAR API. Not sure how I want to approach this yet because I haven't
        spent a ton of time here since those rate limit issues I was having.

        TODO figure out a solution now that my API account works again
    """

    def sec_filings(self, barcount=64, poolsize=5, form_type="8-K", backdate=None):
        """Return tradeable asets with recent SEC filings.

        :param barcount:
        :param poolsize:
        :param form_type:
        :param backdate:
        :return:

        TODO: Move the code in these methods into callbaccks ^ mentioned above
        """
        if not self.edgar_token or self.edgar_token is None:
            raise NotImplementedError

        if not backdate or backdate is None:
            # backdate = time_from_timestamp(time.time() - 604800, time_format="%Y-%m-%d")
            # using a longer window only for debugging purposes -- just to make sure I have results quickly
            backdate = time_from_timestamp(time.time() - (604800 * 26), time_format="%Y-%m-%d")

        date = time_from_timestamp(time.time(), time_format="%Y-%m-%d")

        # Filter the assets down to just those on NASDAQ.
        active_assets = self.broker.get_assets()
        assets = self._tradeable_assets(active_assets)

        print("[-] Going through assets looking for firms with recent SEC filings")
        for i in assets:

            self.get_filings(i, backdate=backdate, date=date, form_type=form_type)

            if len(self.recent_filings.keys()) >= poolsize:
                break
            else:
                continue

        self.tradeable_assets_by_filings(barcount)

        # return self.assets_by_filing

        raise NotImplementedError("[!] SEC parsing needs to be reworked.")

    def get_filings(self, asset, backdate, date, form_type="8-K"):
        """Given a trading entity, get SEC filings in the date range.

        :param asset:
        :param backdate:
        :param date:
        :param form_type:
        :return:
        """
        filings = self.ei.get_sec_filings(asset.symbol, backdate, date, form_type=form_type)

        # If none are found, lengthen the lookback window a couple times
        if filings["total"] is 0:
            print("[!] No recent filings found for {}. Looking back 2 weeks".format(asset.symbol))
            backdate = time_from_timestamp(time.time() - (604800 * 2), time_format="%Y-%m-%d")
            filings = self.ei.get_sec_filings(asset.symbol, backdate, date, form_type=form_type)

        if filings["total"] is 0:
            print("[!] No filings found. Looking back 4 weeks")
            backdate = time_from_timestamp(time.time() - (604800 * 4), time_format="%Y-%m-%d")
            filings = self.ei.get_sec_filings(asset.symbol, backdate, date, form_type=form_type)

        if filings["total"] > 0:
            print("[+] Added:", asset.symbol, " symbols:", len(self.recent_filings.keys()) + 1)
            filings = json.dumps(filings)
            self.recent_filings[asset.symbol] = filings

        raise NotImplementedError("[!] SEC parsing needs to be reworked.")

    def tradeable_assets_by_filings(self, barcount=64):
        """Populate tradeable assets based on discovered SEC filings.

        :return:
        """
        for i in self.recent_filings.keys():
            # I think I need my original 13 week window here for consistency with get_assets_by_candlestick_pattern
            backdate = time_from_timestamp(time.time() - (604800 * 13))

            barset = self.broker.get_barset(i.symbol, "1D", backdate)

            if num_bars(barset[i.symbol], barcount) is False:
                continue

            df = self.broker.extract_bar_data(barset, i.symbol)
            self.assets_by_filing[i.symbol] = df

        raise NotImplementedError("[!] SEC parsing needs to be reworked.")


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
    # backdate        = time_from_timestamp(time.time() - (604800 * 54))
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
        # submit_order(
        #     api_reference=broker.alpaca_api,
        #     ticker=trading_symbol,
        #     qty=quant,
        #     transaction_side="buy",
        #     ttype="market",
        #     time_in_force="ioc"
        # )
