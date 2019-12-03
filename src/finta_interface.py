#!/usr/bin/env python
# -*- coding: utf-8 -*
from pandas.errors import EmptyDataError
from finta import TA

class IndicatorException(Exception):
    pass


class Indicator:

    def __init__(self):
        pass

    @staticmethod
    def get_sma(data):
        """Calculate the simple moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.SMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_smm(data):
        """Calculate the simple moving median for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.SMM(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_ssma(data):
        """Calculate the SMOOTHED simple moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.SSMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_ema(data):
        """Calculate the exponential moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.EMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_dema(data):
        """Calculate the double exponential moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.DEMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_tema(data):
        """Calculate the triple exponential moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.TEMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_trima(data):
        """Calculate the triangular moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.TRIMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_trix(data):
        """Calculate the triple exponential moving average oscillator for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.TRIX(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_vama(data):
        """Calculate the volume adjusted moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.VAMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_er(data):
        """Calculate the Kaufman efficiency ratio for values of given dataframe.

        Example
            bullish: +0.67
            bearish: -0.67

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.ER(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_kama(data):
        """Calculate the Kaufman adaptive moving avarage for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.KAMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_zlema(data):
        """Calculate the zero log exponential moving avarage for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.ZLEMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_wma(data):
        """Calculate the weighted moving avarage for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.WMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_hma(data):
        """Calculate the Hull moving avarage for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.HMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_evwma(data):
        """Calculate the EVWMA for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.EVWMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_vwap(data):
        """Calculate the volume weighted average price for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.VWAP(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_smma(data):
        """Calculate the smoothed moving avarage for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.SMMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_macd(data):
        """Calculate the moving average convergence-divergence for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series with the MACD and signal values
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.MACD(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_ppo(data):
        """Calculate the percentage price oscillator for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series with the PPO and signal values
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.PPO(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_vwmacd(data):
        """Calculate the volume-weighted MACD for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series with the VWMACD and signal values
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.VW_MACD(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_evmacd(data):
        """Calculate the elastic volume-weighted MACD for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series with the EVMACD and signal values
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.EV_MACD(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_mom(data):
        """Calculate the momentum for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.MOM(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_roc(data):
        """Calculate the rate of change for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.ROC(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_rsi(data):
        """Calculate the relative strength index for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.RSI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_ift_rsi(data):
        """Calculate the Inverse-Fisher Transform on relative strength index for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.IFT_RSI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_tr(data):
        """Calculate the true range for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.TR(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_atr(data):
        """Calculate the average true range for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.ATR(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_sar(data):
        """Calculate the stop and reverse for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.SAR(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_bbands(data):
        """Calculate the Bollinger bands for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.BBANDS(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_bbandwidth(data):
        """Calculate the Bollinger bandwidth for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.BBWIDTH(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_percent_b(data):
        """Calculate the percent b for Bollinger band values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.PERCENT_B(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_kc(data):
        """Calculate the Keltner channel of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.KC(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_do(data):
        """Calculate the Donchian channels of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.DO(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_dmi(data):
        """Calculate the directional movement indicator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.DMI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_adx(data):
        """Calculate the ADX of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.ADX(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_pivot(data):
        """Calculate pivot point.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series with 9 elements
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.PIVOT(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_pivot_fib(data):
        """Calculate Fibonacci pivot point.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series with 9 elements
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.PIVOT_FIB(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_stoch(data):
        """Calculate the stochastic oscillator for given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.STOCH(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_stochd(data):
        """Calculate the stochastic oscillator %D for given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.STOCHD(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_stoch_rsi(data):
        """Calculate the stochastic relative strength index for given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.STOCHRSI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_williams(data):
        """Calculate the Williams oscillator for given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.WILLIAMS(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_uo(data):
        """Calculate the ultimate oscillator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.UO(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_ao(data):
        """Calculate the awesome oscillator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.AO(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_mi(data):
        """Calculate the mass index of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.MI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_vortex(data):
        """Calculate the vortex of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.VORTEX(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_kst(data):
        """Calculate the known sure thing oscillator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.KST(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_tsi(data):
        """Calculate the true strength index of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.TSI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_tp(data):
        """Calculate the typical price of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.TP(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_adl(data):
        """Calculate the accumulation/distribution line of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.ADL(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_chaikin(data):
        """Calculate the Chaikin oscillator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.CHAIKIN(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_mfi(data):
        """Calculate the money flow index of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.MFI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_obv(data):
        """Calculate the on balance volume of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.OBV(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_wobv(data):
        """Calculate the weighted on balance volume of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.WOBV(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_vzo(data):
        """Calculate the volume zone oscillator for given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.VZO(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_pzo(data):
        """Calculate the pricing zone oscillator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.PZO(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_efi(data):
        """Calculate the Elder's force index of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.EFI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_cfi(data):
        """Calculate the cumulative force index of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.CFI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_ebbp(data):
        """Calculate the bull power and bear power of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.EBBP(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_emv(data):
        """Calculate the ease of movement of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.EMV(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_cci(data):
        """Calculate the commodity channel index of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.CCI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_copp(data):
        """Calculate the Coppock curve of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.COPP(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_basp(data):
        """Calculate the buying and selling pressure of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.BASP(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_baspn(data):
        """Calculate the normalized buying and selling pressure of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.BASPN(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_cmo(data):
        """Calculate the Chande momentum oscillator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.CMO(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_chandelier(data):
        """Calculate the chandelier exit indicator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.CHANDELIER(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_qstick(data):
        """Calculate the QStick indicator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.QSTICK(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_tmf(data):
        """Calculate the Twigg's money flow of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.TMF(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_wto(data):
        """Calculate the wave trend oscillator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.WTO(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_fish(data):
        """Calculate the Fisher transform of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.FISH(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_ichimoku(data):
        """Calculate the Ichimoku cloud of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.ICHIMOKU(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_apz(data):
        """Calculate the adaptive price zone of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.APZ(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_vr(data):
        """Calculate the vector size indicator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.VR(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_squeeze(data):
        """Calculate the squeeze momentum indicator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.SQZMI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_vpt(data):
        """Calculate the volume price trend of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.VPT(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_fve(data):
        """Calculate the finite volume element of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.FVE(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_vfi(data):
        """Calculate the volume flow indicator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.VFI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_msd(data):
        """Calculate the standard deviation of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("[!] Invalid data value")

        result = TA.MSD(data)
        if result is None:
            raise IndicatorException
        return result
