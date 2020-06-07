#!/usr/bin/env python
# -*- coding: utf-8 -*-
from algos import BaseAlgo
from src.asset_selector import AssetSelector, AssetValidationException


class Algorithm(AssetSelector, BaseAlgo):

    def __init__(self, broker, cli_args):
        super().__init__(broker=broker, cli_args=cli_args, edgar_token=None)

    def bullish_gainers_and_losers(self):
        """
        Use Polygon endpoint to populate a watchlist of top gainers and losers.
        """
        if not self.poolsize or self.poolsize is None or self.poolsize is 0:
            raise AssetValidationException("[!] Invalid pool size.")

        self.portfolio = []

        gainers = self.broker.api.polygon.gainers_losers()
        losers = self.broker.api.polygon.gainers_losers("losers")
        for symbol in range(len(gainers)):

            ticker = gainers[symbol].ticker
            ass = self.broker.get_asset(ticker)
            if ass is not None and ass.tradable and ass.easy_to_borrow:

                # TODO: look for reversal here

                # add the current symbol to the portfolio
                self.portfolio.append(ass.symbol)
                if len(self.portfolio) >= self.poolsize:
                    # exit the filter process
                    break

        for symbol in range(len(losers)):

            ticker = losers[symbol].ticker
            ass = self.broker.get_asset(ticker)
            if ass is not None and ass.tradable and ass.easy_to_borrow:

                # TODO: look for reversal here

                # add the current symbol to the portfolio
                self.portfolio.append(ass.symbol)
                if len(self.portfolio) >= self.poolsize:
                    # exit the filter process
                    break

    def get_ratings(self, algo_time=None, window_size=5):
        pass

    def portfolio_allocation(self, data, cash):
        pass

    def total_asset_value(self, positions, date):
        pass

def run(broker, args):
    pass
