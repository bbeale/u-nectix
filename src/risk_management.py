#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

"""
https://towardsdatascience.com/building-an-automated-trading-system-from-the-comfort-of-your-own-home-c9a2fb7405a3#Risk%20Management


https://pyportfolioopt.readthedocs.io/en/latest/
"""

class RiskManagement:

    def __init__(self, dataframe):

        self.dataframe = dataframe
        # Calculate expected returns and sample covariance
        self.mu = expected_returns.mean_historical_return(self.dataframe)
        self.S = risk_models.sample_cov(self.dataframe)
        # Optimise for maximal Sharpe ratio
        self.ef = EfficientFrontier(self.mu, self.S)
        self.weights = self.ef.max_sharpe()
        self.ef.portfolio_performance(verbose=True)

    @staticmethod
    def get_max_drawdown(data):
        if data is None or len(data.keys()) < 1:
            raise RiskManagementException

        # result = max_drawdown(data)
        # return result if result is not None else None
        raise NotImplementedError

    def risk_management(self):
        raise NotImplementedError


class RiskManagementException(Exception):
    pass
