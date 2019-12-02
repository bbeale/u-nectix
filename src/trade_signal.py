#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.indicator_getter import IndicatorGetter as IG, IndicatorGetterException as IGError

class TradeSignalException(Exception):
    pass


class TradeSignal:

    def __init__(self):
        pass

    @staticmethod
    def macd_buy(dataframe):
        """Calculate a moving average convergence-divergence buy signal from a bullish signal crossover.

        :param dataframe:
        :return:
        """
        try:
            raw_macd = IG.get_macd(dataframe)
        except IGError:
            raise IGError("[!] Failed to retrieve raw MACD values")

        try:
            macd_buysignal = raw_macd["MACD"].iloc[-1] < 0 and min(raw_macd["MACD"].iloc[-4:-2]) < raw_macd["SIGNAL"].iloc[-1] and raw_macd["MACD"].iloc[-1] > \
                             raw_macd["SIGNAL"].iloc[-1]
        except IndexError:
            raise TradeSignalException
        else:
            return macd_buysignal

    @staticmethod
    def mfi_buy(dataframe):
        """Calculate a money flow index buy signal from a bullish crossover over the 10 mark.

        :param dataframe:
        :return:
        """
        try:
            raw_mfi = IG.get_mfi(dataframe)
        except IGError:
            raise IGError("[!] Failed to retrieve raw MFI values")

        try:
            mfi_buysignal = raw_mfi.iloc[-1] > 10 and min(raw_mfi.iloc[-4:-2]) <= 10
        except IndexError:
            raise TradeSignalException
        else:
            return mfi_buysignal

    @staticmethod
    def vzo_buy(dataframe):
        """Calculate a volatility zone oscillator buy signal from a bullish crossover over the -40 mark.

        :param dataframe:
        :return:
        """
        try:
            raw_vzo = IG.get_vzo(dataframe)
        except IGError:
            raise IGError("[!] Failed to retrieve raw VZO values")

        try:
            vzo_buysignal = raw_vzo.iloc[-1] > -40 and min(raw_vzo.iloc[-4:-2]) <= -40
        except IndexError:
            raise TradeSignalException
        else:
            return vzo_buysignal

    @staticmethod
    def stoch_buy(dataframe):
        """Calculate a stochastic oscillator buy signal from a bullish crossover over the 10 mark.

        :param dataframe:
        :return:
        """
        try:
            raw_stoch = IG.get_stoch(dataframe)
        except IGError:
            raise IGError("[!] Failed to retrieve raw stochastic oscillator values")

        try:
            stoch_buysignal = raw_stoch.iloc[-1] > 10 and min(raw_stoch.iloc[-4:-2]) <= 10
        except IndexError:
            raise TradeSignalException
        else:
            return stoch_buysignal

    @staticmethod
    def macd_sell(dataframe):
        raise NotImplementedError

    @staticmethod
    def mfi_sell(dataframe):
        raise NotImplementedError

    @staticmethod
    def vzo_sell(dataframe):
        raise NotImplementedError

    @staticmethod
    def stoch_sell(dataframe):
        raise NotImplementedError
