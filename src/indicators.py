#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.indicator_getter import IndicatorGetter as IG, IndicatorGetterException as IGError
from util import time_formatter, set_candlestick_df
from requests.exceptions import HTTPError
from pandas.errors import EmptyDataError
import src.twitter_interface as twitter
import time

class IndicatorException(Exception):
    pass


class Indicators:

    def __init__(self, alpaca_api_interface, dataframe=None):

        if not alpaca_api_interface or alpaca_api_interface is None:
            raise ValueError("[!] Alpaca API interface instance required")
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
            raise ValueError("[!] Invalid ticker value")

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        bars = self.get_bars(ticker, backdate)
        data = set_candlestick_df(bars)

        try:
            # grab individual indicator values
            data["sma"]                 = IG.get_sma(data)
            data["smm"]                 = IG.get_smm(data)
            data["ssma"]                = IG.get_ssma(data)
            data["ema"]                 = IG.get_ema(data)
            data["dema"]                = IG.get_dema(data)
            data["tema"]                = IG.get_tema(data)
            data["trima"]               = IG.get_trima(data)
            data["trix"]                = IG.get_trix(data)
            data["vama"]                = IG.get_vama(data)
            data["er"]                  = IG.get_er(data)
            data["kama"]                = IG.get_kama(data)
            data["zlema"]               = IG.get_zlema(data)
            data["wma"]                 = IG.get_wma(data)
            data["wma"]                 = IG.get_wma(data)
            data["vwap"]                = IG.get_vwap(data)
            data["smma"]                = IG.get_smma(data)
            macd                        = IG.get_macd(data)
            data["macd"]                = macd["MACD"]
            data["signal"]              = macd["SIGNAL"]
            ppo                         = IG.get_ppo(data)
            data["ppo"]                 = ppo["PPO"]
            data["ppo_sig"]             = ppo["SIGNAL"]
            data["ppo_histo"]           = ppo["HISTO"]
            vwmacd                      = IG.get_vwmacd(data)
            data["vwmacd"]              = vwmacd["MACD"]
            data["vwsignal"]            = vwmacd["SIGNAL"]
            data["mom"]                 = IG.get_mom(data)
            data["roc"]                 = IG.get_roc(data)
            data["rsi"]                 = IG.get_rsi(data)
            data["ift_rsi"]             = IG.get_ift_rsi(data)
            data["tr"]                  = IG.get_tr(data)
            data["atr"]                 = IG.get_atr(data)
            data["sar"]                 = IG.get_sar(data)
            bbands                      = IG.get_bbands(data)
            data["bb_up"]               = bbands["BB_UPPER"]
            data["bb_mid"]              = bbands["BB_MIDDLE"]
            data["bb_low"]              = bbands["BB_LOWER"]
            data["bandwidth"]           = IG.get_bbandwidth(data)
            data["percent_b"]           = IG.get_percent_b(data)
            kc                          = IG.get_kc(data)
            data["kc_up"]               = kc["KC_UPPER"]
            data["kc_low"]              = kc["KC_LOWER"]
            pivot                       = IG.get_pivot(data)
            data["pivot"]               = pivot["pivot"]
            data["pivot_s1"]            = pivot["s1"]
            data["pivot_s2"]            = pivot["s2"]
            data["pivot_s3"]            = pivot["s3"]
            data["pivot_s4"]            = pivot["s4"]
            data["pivot_r1"]            = pivot["r1"]
            data["pivot_r2"]            = pivot["r2"]
            data["pivot_r3"]            = pivot["r3"]
            data["pivot_r4"]            = pivot["r4"]
            pivot_fib                   = IG.get_pivot_fib(data)
            data["pivot_fib"]           = pivot_fib["pivot"]
            data["pivot_fib_s1"]        = pivot_fib["s1"]
            data["pivot_fib_s2"]        = pivot_fib["s2"]
            data["pivot_fib_s3"]        = pivot_fib["s3"]
            data["pivot_fib_s4"]        = pivot_fib["s4"]
            data["pivot_fib_r1"]        = pivot_fib["r1"]
            data["pivot_fib_r2"]        = pivot_fib["r2"]
            data["pivot_fib_r3"]        = pivot_fib["r3"]
            data["pivot_fib_r4"]        = pivot_fib["r4"]
            data["stoch"]               = IG.get_stoch(data)
            data["stochd"]              = IG.get_stochd(data)
            data["stoch_rsi"]           = IG.get_stoch_rsi(data)
            data["williams"]            = IG.get_williams(data)
            data["uo"]                  = IG.get_uo(data)
            data["ao"]                  = IG.get_ao(data)
            data["mi"]                  = IG.get_mi(data)
            vortex                      = IG.get_vortex(data)
            data["vortex_p"]            = vortex["VIp"]
            data["vortex_m"]            = vortex["VIm"]
            kst                         = IG.get_kst(data)
            data["kst"]                 = kst["KST"]
            data["kst_sig"]             = kst["signal"]
            tsi                         = IG.get_tsi(data)
            data["tsi"]                 = tsi["TSI"]
            data["tsi_sig"]             = tsi["signal"]
            data["tp"]                  = IG.get_tp(data)
            data["adl"]                 = IG.get_adl(data)
            data["chaikin"]             = IG.get_chaikin(data)
            data["mfi"]                 = IG.get_mfi(data)
            data["obv"]                 = IG.get_obv(data)
            data["wobv"]                = IG.get_wobv(data)
            data["vzo"]                 = IG.get_vzo(data)
            data["pzo"]                 = IG.get_pzo(data)
            data["efi"]                 = IG.get_efi(data)
            data["cfi"]                 = IG.get_cfi(data)
            ebbp                        = IG.get_ebbp(data)
            data["ebbp_bull"]           = ebbp["Bull."]
            data["ebbp_bear"]           = ebbp["Bear."]
            data["emv"]                 = IG.get_emv(data)
            data["cci"]                 = IG.get_cci(data)
            data["copp"]                = IG.get_copp(data)
            basp                        = IG.get_basp(data)
            data["basp_buy"]            = basp["Buy."]
            data["basp_sell"]           = basp["Sell."]
            baspn                       = IG.get_baspn(data)
            data["baspn_buy"]           = baspn["Buy."]
            data["baspn_sell"]          = baspn["Sell."]
            data["cmo"]                 = IG.get_cmo(data)
            chandelier                  = IG.get_chandelier(data)
            data["chand_long"]          = chandelier["Long."]
            data["chand_short"]         = chandelier["Short."]
            data["qstick"]              = IG.get_qstick(data)
            wto                         = IG.get_wto(data)
            data["wt1"]                 = wto["WT1."]
            data["wt2"]                 = wto["WT2."]
            data["fish"]                = IG.get_fish(data)
            ichi                        = IG.get_ichimoku(data)
            data["tenkan"]              = ichi["TENKAN"]
            data["kijun"]               = ichi["KIJUN"]
            data["senkou_span_a"]       = ichi["senkou_span_a"]
            data["senkou_span_b"]       = ichi["SENKOU"]
            data["chikou"]              = ichi["CHIKOU"]
            apz                         = IG.get_apz(data)
            data["apz_up"]              = apz["UPPER"]
            data["apz_low"]             = apz["LOWER"]
            data["squeeze"]             = IG.get_squeeze(data)
            data["vpt"]                 = IG.get_vpt(data)
            data["fve"]                 = IG.get_fve(data)
            data["vfi"]                 = IG.get_fve(data)
            data["msd"]                 = IG.get_msd(data)

            # TODO: Add Twitter / sentiment scores, empyrical data, other fundamentals

        except IGError:
            print("[?] Failed to grab one or more indicator for {}".format(ticker))
        else:
            return data

    def get_bars(self, ticker, backdate=None):
        """Get bars for a ticker symbol

        :param ticker: a stock ticker symbol
        :param backdate: start of the historic data lookup period. If none, defaults to the last 13 weeks (1 quarter)
        :return: dataframe built from barset objects, including indicators
        """
        if not ticker or ticker is None:
            raise ValueError("[!] Invalid ticker value")

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))
        bars = None
        try:
            bars = self.api.get_barset(ticker, "1D", after=backdate)[ticker]
        except HTTPError:
            print("\tRetrying...")
            time.sleep(3)
            try:
                bars = self.api.get_barset(ticker, "1D", after=backdate)[ticker]
            except HTTPError:
                raise HTTPError
        finally:
            return bars
