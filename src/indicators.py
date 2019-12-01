#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import time_formatter, set_candlestick_df
from requests.exceptions import HTTPError
from pandas.errors import EmptyDataError
from finta import TA
import time


class IndicatorException(Exception):
    pass


class Indicators:

    def __init__(self, alpaca_api_interface, dataframe=None):

        if not alpaca_api_interface or alpaca_api_interface is None:
            raise ValueError("Alpaca API interface instance required")
        self.api            = alpaca_api_interface
        self.account        = self.api.get_account()
        self.buying_power   = self.account.buying_power
        self.dataframe      = dataframe

    def get_all_asset_indicators(self, backdate=None):
        """Loop through collection of assets and append their indicators to the dataframe.

        :return: A pandas dataframe of ticker dataframes for each asset.
        """
        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        for ticker in self.dataframe.keys():
            try:
                self.dataframe[ticker] = self.get_ticker_indicators(ticker, backdate=backdate)
            except EmptyDataError:
                raise EmptyDataError
            except IndicatorException:
                raise IndicatorException
            else:
                continue
        return self.dataframe

    def get_ticker_indicators(self, ticker, backdate=None):
        """Given a ticker symbol and a backdate, calculate indicator values and add them to a dataframe.

        :param ticker: A stock ticker value
        :param backdate: A date to look back. Will default to 13 weeks ago (1 quarter) if None.
        :return: a pandas dataframe with OHLC + indicator values.
        """
        if not ticker or ticker is None:
            raise ValueError("Invalid ticker value")

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        bars                        = self.get_bars(ticker, backdate)
        data                        = set_candlestick_df(bars)

        try:
            # grab individual indicator values
            data["sma"]                 = self.get_sma(data)
            data["smm"]                 = self.get_smm(data)
            data["ssma"]                = self.get_ssma(data)
            data["ema"]                 = self.get_ema(data)
            data["dema"]                = self.get_dema(data)
            data["tema"]                = self.get_tema(data)
            data["trima"]               = self.get_trima(data)
            data["trix"]                = self.get_trix(data)
            data["vama"]                = self.get_vama(data)
            data["er"]                  = self.get_er(data)
            data["kama"]                = self.get_kama(data)
            data["zlema"]               = self.get_zlema(data)
            data["wma"]                 = self.get_wma(data)
            data["wma"]                 = self.get_wma(data)
            data["vwap"]                = self.get_vwap(data)
            data["smma"]                = self.get_smma(data)
            macd                        = self.get_macd(data)
            data["macd"]                = macd["MACD"]
            data["signal"]              = macd["SIGNAL"]
            ppo                         = self.get_ppo(data)
            data["ppo"]                 = ppo["PPO"]
            data["ppo_sig"]             = ppo["SIGNAL"]
            data["ppo_histo"]           = ppo["HISTO"]
            vwmacd                      = self.get_vwmacd(data)
            data["vwmacd"]              = vwmacd["MACD"]
            data["vwsignal"]            = vwmacd["SIGNAL"]
            data["mom"]                 = self.get_mom(data)
            data["roc"]                 = self.get_roc(data)
            data["rsi"]                 = self.get_rsi(data)
            data["ift_rsi"]             = self.get_ift_rsi(data)
            data["tr"]                  = self.get_tr(data)
            data["atr"]                 = self.get_atr(data)
            data["sar"]                 = self.get_sar(data)
            bbands                      = self.get_bbands(data)
            data["bb_up"]               = bbands["BB_UPPER"]
            data["bb_mid"]              = bbands["BB_MIDDLE"]
            data["bb_low"]              = bbands["BB_LOWER"]
            data["bandwidth"]           = self.get_bbandwidth(data)
            data["percent_b"]           = self.get_percent_b(data)
            kc                          = self.get_kc(data)
            data["kc_up"]               = kc["KC_UPPER"]
            data["kc_low"]              = kc["KC_LOWER"]
            pivot                       = self.get_pivot(data)
            data["pivot"]               = pivot["pivot"]
            data["pivot_s1"]            = pivot["s1"]
            data["pivot_s2"]            = pivot["s2"]
            data["pivot_s3"]            = pivot["s3"]
            data["pivot_s4"]            = pivot["s4"]
            data["pivot_r1"]            = pivot["r1"]
            data["pivot_r2"]            = pivot["r2"]
            data["pivot_r3"]            = pivot["r3"]
            data["pivot_r4"]            = pivot["r4"]
            pivot_fib                   = self.get_pivot_fib(data)
            data["pivot_fib"]           = pivot_fib["pivot"]
            data["pivot_fib_s1"]        = pivot_fib["s1"]
            data["pivot_fib_s2"]        = pivot_fib["s2"]
            data["pivot_fib_s3"]        = pivot_fib["s3"]
            data["pivot_fib_s4"]        = pivot_fib["s4"]
            data["pivot_fib_r1"]        = pivot_fib["r1"]
            data["pivot_fib_r2"]        = pivot_fib["r2"]
            data["pivot_fib_r3"]        = pivot_fib["r3"]
            data["pivot_fib_r4"]        = pivot_fib["r4"]
            data["stoch"]               = self.get_stoch(data)
            data["stochd"]              = self.get_stochd(data)
            data["stoch_rsi"]           = self.get_stoch_rsi(data)
            data["williams"]            = self.get_williams(data)
            data["uo"]                  = self.get_uo(data)
            data["ao"]                  = self.get_ao(data)
            data["mi"]                  = self.get_mi(data)
            vortex                      = self.get_vortex(data)
            data["vortex_p"]            = vortex["VIp"]
            data["vortex_m"]            = vortex["VIm"]
            kst                         = self.get_kst(data)
            data["kst"]                 = kst["KST"]
            data["kst_sig"]             = kst["signal"]
            tsi                         = self.get_tsi(data)
            data["tsi"]                 = tsi["TSI"]
            data["tsi_sig"]             = tsi["signal"]
            data["tp"]                  = self.get_tp(data)
            data["adl"]                 = self.get_adl(data)
            data["chaikin"]             = self.get_chaikin(data)
            data["mfi"]                 = self.get_mfi(data)
            data["obv"]                 = self.get_obv(data)
            data["wobv"]                = self.get_wobv(data)
            data["vzo"]                 = self.get_vzo(data)
            data["pzo"]                 = self.get_pzo(data)
            data["efi"]                 = self.get_efi(data)
            data["cfi"]                 = self.get_cfi(data)
            ebbp                        = self.get_ebbp(data)
            data["ebbp_bull"]           = ebbp["Bull."]
            data["ebbp_bear"]           = ebbp["Bear."]
            data["emv"]                 = self.get_emv(data)
            data["cci"]                 = self.get_cci(data)
            data["copp"]                = self.get_copp(data)
            basp                        = self.get_basp(data)
            data["basp_buy"]            = basp["Buy."]
            data["basp_sell"]           = basp["Sell."]
            baspn                       = self.get_baspn(data)
            data["baspn_buy"]           = baspn["Buy."]
            data["baspn_sell"]          = baspn["Sell."]
            data["cmo"]                 = self.get_cmo(data)
            chandelier                  = self.get_chandelier(data)
            data["chand_long"]          = chandelier["Long."]
            data["chand_short"]         = chandelier["Short."]
            data["qstick"]              = self.get_qstick(data)
            wto                         = self.get_wto(data)
            data["wt1"]                 = wto["WT1."]
            data["wt2"]                 = wto["WT2."]
            data["fish"]                = self.get_fish(data)
            ichi                        = self.get_ichimoku(data)
            data["tenkan"]              = ichi["TENKAN"]
            data["kijun"]               = ichi["KIJUN"]
            data["senkou_span_a"]       = ichi["senkou_span_a"]
            data["senkou_span_b"]       = ichi["SENKOU"]
            data["chikou"]              = ichi["CHIKOU"]
            apz                         = self.get_apz(data)
            data["apz_up"]              = apz["UPPER"]
            data["apz_low"]             = apz["LOWER"]
            data["squeeze"]             = self.get_squeeze(data)
            data["vpt"]                 = self.get_vpt(data)
            data["fve"]                 = self.get_fve(data)
            data["vfi"]                 = self.get_fve(data)
            data["msd"]                 = self.get_msd(data)

        except IndicatorException:
            print("[?] Lets see what just continuing does...")
        else:
            return data

    def get_bars(self, ticker, backdate=None):
        """Get bars for a ticker symbol

        :param ticker: a stock ticker symbol
        :param backdate: start of the historic data lookup period. If none, defaults to the last 13 weeks (1 quarter)
        :return: dataframe built from barset objects, including indicators
        """
        if not ticker or ticker is None:
            raise ValueError("Invalid ticker value")

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))
        bars = None
        try:
            bars = self.api.get_barset(ticker, "1D", after=backdate)[ticker]
        except HTTPError:
            print("Retrying...")
            time.sleep(3)
            try:
                bars = self.api.get_barset(ticker, "1D", after=backdate)[ticker]
            except HTTPError:
                raise HTTPError
        finally:
            return bars

    @staticmethod
    def get_sma(data):
        """Calculate the simple moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

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
            raise EmptyDataError("Invalid data value")

        result = TA.MSD(data)
        if result is None:
            raise IndicatorException
        return result
