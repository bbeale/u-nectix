#!/usr/bin/env python
# -*- coding: utf-8 -*-


class AlgoException(Exception):
    pass


class BaseAlgo:

    def __init__(self):
        pass

    def get_ratings(self, algo_time=None, window_size=5):
        raise NotImplementedError

    def portfolio_allocation(self, data, cash):
        raise NotImplementedError
