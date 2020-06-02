#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.finta_interface import Indicator, IndicatorException
from broker import BrokerException
from pandas.errors import EmptyDataError
from util import time_from_timestamp
import pandas as pd
import inspect
import time


class Indicators:

    def __init__(self, broker, cli_args, asset_selector=None, backdate=None):
        """
        :param broker:
        :param cli_args:
        :param asset_selector:
        :param backdate:
        """
        if not broker or broker is None:
            raise IndicatorValidationException('[!] Broker instance required.')

        if asset_selector is not None:
            self.portfolio = asset_selector.portfolio
        else:
            raise IndicatorValidationException('[!] No ticker symbols found to trade.')

        if not backdate or backdate is None:
            backdate = time_from_timestamp(time.time() - (604800 * 54))

        if cli_args.period is not None:
            self.period = cli_args.period
        else:
            self.period = '1D'

        self.all_indicators = True
        self.broker         = broker
        self.backdate       = backdate
        self.indicator_list = None
        self.mode           = cli_args.mode
        self.account        = self.broker.trading_account
        self.buying_power   = self.broker.buying_power
        self.data           = dict()
        self.model_data     = pd.DataFrame()

        # init stage two:
        self._populate_indicators()

    def _populate_indicators(self):
        """ Second method of two stage init process. """
        self.indicator_list = []
        self._asset_indicators()

    def _asset_indicators(self, backdate=None):
        """Loop through collection of assets and append their indicators to the dataframe.

        :return: A pandas dataframe of ticker dataframes for each asset.
        """
        if not backdate or backdate is None:
            print('[Debug] Backdate debug', inspect.stack()[0][3])
            backdate = time_from_timestamp(time.time() - (604800 * 13))

        for ticker in self.portfolio:
            try:
                self.data[ticker] = self.get_ticker_indicators(ticker, self.period)
            except EmptyDataError:
                raise EmptyDataError
            except IndicatorException:
                raise IndicatorException
            else:
                continue
        return self.data

    def get_ticker_indicators(self, ticker, period, backdate=None, _limit=1000):
        """Given a ticker symbol and a backdate, calculate indicator values and add them to a dataframe.

        :param ticker: A stock ticker value
        :param period: a date period. Valid values are minute, 1Min, 5Min, 15Min, day or 1D
        :param backdate: A date to look back. Will default to 13 weeks ago (1 quarter) if None.
        :param _limit:
        :return: a pandas dataframe with OHLC + indicator values.
        """
        if not ticker or ticker is None:
            raise IndicatorValidationException('[!] Invalid ticker.')

        if not period or period is None:
            raise IndicatorValidationException('[!] Invalid period.')

        if backdate is not None:
            try:
                data = self.broker.get_barset_df(ticker, period, backdate=backdate, limit=_limit)
            except BrokerException:
                raise BrokerException('[!] Error getting bars.')

        else:
            try:
                data = self.broker.get_barset_df(ticker, period, limit=_limit)
            except BrokerException:
                raise BrokerException('[!] Error getting bars.')

        if not self.all_indicators:
            if self.indicator_list is None or len(self.indicator_list) < 1:
                # use a random default set of indicators
                try:
                    macd                        = Indicator.get_macd(data)
                    data['macd']                = macd['MACD']
                    data['signal']              = macd['SIGNAL']
                    data['mfi']                 = Indicator.get_mfi(data)
                    data['vzo']                 = Indicator.get_vzo(data)

                    self.indicator_list = ['macd', 'signal', 'mfi', 'vzo']
                except IndicatorException:
                    print('[?] Failed to grab one or more indicator for {}'.format(ticker))

        else:
            i_list = []
            try:
                if 'sma' in self.indicator_list or self.all_indicators:
                    i_list.append('sma')
                    data['sma'] = Indicator.get_sma(data)
                if 'smm' in self.indicator_list or self.all_indicators:
                    i_list.append('smm')
                    data['smm'] = Indicator.get_smm(data)
                if 'ssma' in self.indicator_list or self.all_indicators:
                    i_list.append('ssma')
                    data['ssma'] = Indicator.get_ssma(data)
                if 'ema' in self.indicator_list or self.all_indicators:
                    i_list.append('ema')
                    data['ema'] = Indicator.get_ema(data)
                if 'dema' in self.indicator_list or self.all_indicators:
                    i_list.append('dema')
                    data['dema'] = Indicator.get_dema(data)
                if 'tema' in self.indicator_list or self.all_indicators:
                    i_list.append('tema')
                    data['tema'] = Indicator.get_tema(data)
                if 'trima' in self.indicator_list or self.all_indicators:
                    i_list.append('trima')
                    data['trima'] = Indicator.get_trima(data)
                if 'trix' in self.indicator_list or self.all_indicators:
                    i_list.append('trix')
                    data['trix'] = Indicator.get_trix(data)
                if 'vama' in self.indicator_list or self.all_indicators:
                    i_list.append('vama')
                    data['vama'] = Indicator.get_vama(data)
                if 'er' in self.indicator_list or self.all_indicators:
                    i_list.append('er')
                    data['er'] = Indicator.get_er(data)
                if 'kama' in self.indicator_list or self.all_indicators:
                    i_list.append('kama')
                    data['kama'] = Indicator.get_kama(data)
                if 'zlema' in self.indicator_list or self.all_indicators:
                    i_list.append('zlema')
                    data['zlema'] = Indicator.get_zlema(data)
                if 'wma' in self.indicator_list or self.all_indicators:
                    i_list.append('wma')
                    data['wma'] = Indicator.get_wma(data)
                if 'vwap' in self.indicator_list or self.all_indicators:
                    i_list.append('vwap')
                    data['vwap'] = Indicator.get_vwap(data)
                if 'smma' in self.indicator_list or self.all_indicators:
                    i_list.append('smma')
                    data['smma'] = Indicator.get_smma(data)
                if 'macd' in self.indicator_list or self.all_indicators:
                    i_list.append('macd')
                    macd = Indicator.get_macd(data)
                    data['macd'] = macd['MACD']
                    data['signal'] = macd['SIGNAL']
                if 'ppo' in self.indicator_list or self.all_indicators:
                    i_list.append('ppo')
                    ppo = Indicator.get_ppo(data)
                    data['ppo'] = ppo['PPO']
                    data['ppo_sig'] = ppo['SIGNAL']
                    data['ppo_histo'] = ppo['HISTO']
                if 'vwmacd' in self.indicator_list or self.all_indicators:
                    i_list.append('vwmacd')
                    vwmacd = Indicator.get_vwmacd(data)
                    data['vwmacd'] = vwmacd['MACD']
                    data['vwsignal'] = vwmacd['SIGNAL']
                if 'mom' in self.indicator_list or self.all_indicators:
                    i_list.append('mom')
                    data['mom'] = Indicator.get_mom(data)
                if 'roc' in self.indicator_list or self.all_indicators:
                    i_list.append('roc')
                    data['roc'] = Indicator.get_roc(data)
                if 'rsi' in self.indicator_list or self.all_indicators:
                    i_list.append('rsi')
                    data['rsi'] = Indicator.get_rsi(data)
                if 'ift_rsi' in self.indicator_list or self.all_indicators:
                    i_list.append('ift_rsi')
                    data['ift_rsi'] = Indicator.get_ift_rsi(data)
                if 'tr' in self.indicator_list or self.all_indicators:
                    i_list.append('tr')
                    data['tr'] = Indicator.get_tr(data)
                if 'atr' in self.indicator_list or self.all_indicators:
                    i_list.append('atr')
                    data['atr'] = Indicator.get_atr(data)
                if 'sar' in self.indicator_list or self.all_indicators:
                    i_list.append('sar')
                    data['sar'] = Indicator.get_sar(data)
                if 'bb' in self.indicator_list or self.all_indicators:
                    i_list.append('bb')
                    bbands = Indicator.get_bbands(data)
                    data['bb_up'] = bbands['BB_UPPER']
                    data['bb_mid'] = bbands['BB_MIDDLE']
                    data['bb_low'] = bbands['BB_LOWER']
                if 'bandwidth' in self.indicator_list or self.all_indicators:
                    i_list.append('bandwidth')
                    data['bandwidth'] = Indicator.get_bbandwidth(data)
                if 'percent_b' in self.indicator_list or self.all_indicators:
                    i_list.append('percent_b')
                    data['percent_b'] = Indicator.get_percent_b(data)
                if 'kc' in self.indicator_list or self.all_indicators:
                    i_list.append('kc')
                    kc = Indicator.get_kc(data)
                    data['kc_up'] = kc['KC_UPPER']
                    data['kc_low'] = kc['KC_LOWER']
                if 'pivot' in self.indicator_list or self.all_indicators:
                    i_list.append('pivot')
                    pivot = Indicator.get_pivot(data)
                    data['pivot'] = pivot['pivot']
                    data['pivot_s1'] = pivot['s1']
                    data['pivot_s2'] = pivot['s2']
                    data['pivot_s3'] = pivot['s3']
                    data['pivot_s4'] = pivot['s4']
                    data['pivot_r1'] = pivot['r1']
                    data['pivot_r2'] = pivot['r2']
                    data['pivot_r3'] = pivot['r3']
                    data['pivot_r4'] = pivot['r4']
                if 'pivot_fib' in self.indicator_list or self.all_indicators:
                    i_list.append('pivot_fib')
                    pivot_fib = Indicator.get_pivot_fib(data)
                    data['pivot_fib'] = pivot_fib['pivot']
                    data['pivot_fib_s1'] = pivot_fib['s1']
                    data['pivot_fib_s2'] = pivot_fib['s2']
                    data['pivot_fib_s3'] = pivot_fib['s3']
                    data['pivot_fib_s4'] = pivot_fib['s4']
                    data['pivot_fib_r1'] = pivot_fib['r1']
                    data['pivot_fib_r2'] = pivot_fib['r2']
                    data['pivot_fib_r3'] = pivot_fib['r3']
                    data['pivot_fib_r4'] = pivot_fib['r4']
                if 'stoch' in self.indicator_list or self.all_indicators:
                    i_list.append('stoch')
                    data['stoch'] = Indicator.get_stoch(data)
                if 'stochd' in self.indicator_list or self.all_indicators:
                    i_list.append('stochd')
                    data['stochd'] = Indicator.get_stochd(data)
                if 'stoch_rsi' in self.indicator_list or self.all_indicators:
                    i_list.append('stoch_rsi')
                    data['stoch_rsi'] = Indicator.get_stoch_rsi(data)
                if 'williams' in self.indicator_list or self.all_indicators:
                    i_list.append('williams')
                    data['williams'] = Indicator.get_williams(data)
                if 'uo' in self.indicator_list or self.all_indicators:
                    i_list.append('uo')
                    data['uo'] = Indicator.get_uo(data)
                if 'ao' in self.indicator_list or self.all_indicators:
                    i_list.append('ao')
                    data['ao'] = Indicator.get_ao(data)
                if 'mi' in self.indicator_list or self.all_indicators:
                    i_list.append('mi')
                    data['mi'] = Indicator.get_mi(data)
                if 'vortex_p' in self.indicator_list or self.all_indicators:
                    i_list.append('vortex_p')
                    vortex = Indicator.get_vortex(data)
                    data['vortex_p'] = vortex['VIp']
                    data['vortex_m'] = vortex['VIm']
                if 'kst' in self.indicator_list or self.all_indicators:
                    i_list.append('kst')
                    kst = Indicator.get_kst(data)
                    data['kst'] = kst['KST']
                    data['kst_sig'] = kst['signal']
                if 'tsi' in self.indicator_list or self.all_indicators:
                    i_list.append('tsi')
                    tsi = Indicator.get_tsi(data)
                    data['tsi'] = tsi['TSI']
                    data['tsi_sig'] = tsi['signal']
                if 'tp' in self.indicator_list or self.all_indicators:
                    i_list.append('tp')
                    data['tp'] = Indicator.get_tp(data)
                if 'adl' in self.indicator_list or self.all_indicators:
                    i_list.append('adl')
                    data['adl'] = Indicator.get_adl(data)
                if 'chaikin' in self.indicator_list or self.all_indicators:
                    i_list.append('chaikin')
                    data['chaikin'] = Indicator.get_chaikin(data)
                if 'mfi' in self.indicator_list or self.all_indicators:
                    i_list.append('mfi')
                    data['mfi'] = Indicator.get_mfi(data)
                if 'obv' in self.indicator_list or self.all_indicators:
                    i_list.append('obv')
                    data['obv'] = Indicator.get_obv(data)
                if 'wobv' in self.indicator_list or self.all_indicators:
                    i_list.append('wobv')
                    data['wobv'] = Indicator.get_wobv(data)
                if 'vzo' in self.indicator_list or self.all_indicators:
                    i_list.append('vzo')
                    data['vzo'] = Indicator.get_vzo(data)
                if 'pzo' in self.indicator_list or self.all_indicators:
                    i_list.append('pzo')
                    data['pzo'] = Indicator.get_pzo(data)
                if 'efi' in self.indicator_list or self.all_indicators:
                    i_list.append('efi')
                    data['efi'] = Indicator.get_efi(data)
                if 'cfi' in self.indicator_list or self.all_indicators:
                    i_list.append('cfi')
                    data['cfi'] = Indicator.get_cfi(data)
                if 'ebbp' in self.indicator_list or self.all_indicators:
                    i_list.append('ebbp')
                    ebbp = Indicator.get_ebbp(data)
                    data['ebbp_bull'] = ebbp['Bull.']
                    data['ebbp_bear'] = ebbp['Bear.']
                if 'emv' in self.indicator_list or self.all_indicators:
                    i_list.append('emv')
                    data['emv'] = Indicator.get_emv(data)
                if 'cci' in self.indicator_list or self.all_indicators:
                    i_list.append('cci')
                    data['cci'] = Indicator.get_cci(data)
                if 'copp' in self.indicator_list or self.all_indicators:
                    i_list.append('copp')
                    data['copp'] = Indicator.get_copp(data)
                if 'basp' in self.indicator_list or self.all_indicators:
                    i_list.append('basp')
                    basp = Indicator.get_basp(data)
                    data['basp_buy'] = basp['Buy.']
                    data['basp_sell'] = basp['Sell.']
                if 'cmo' in self.indicator_list or self.all_indicators:
                    i_list.append('cmo')
                    data['cmo'] = Indicator.get_cmo(data)
                if 'chand' in self.indicator_list or self.all_indicators:
                    i_list.append('chand')
                    chandelier = Indicator.get_chandelier(data)
                    data['chand_long'] = chandelier['Long.']
                    data['chand_short'] = chandelier['Short.']
                if 'qstick' in self.indicator_list or self.all_indicators:
                    i_list.append('qstick')
                    data['qstick'] = Indicator.get_qstick(data)
                if 'wto' in self.indicator_list or self.all_indicators:
                    i_list.append('wto')
                    wto = Indicator.get_wto(data)
                    data['wt1'] = wto['WT1.']
                    data['wt2'] = wto['WT2.']
                if 'fish' in self.indicator_list or self.all_indicators:
                    i_list.append('fish')
                    data['fish'] = Indicator.get_fish(data)
                if 'tenkan' in self.indicator_list or self.all_indicators:
                    i_list.append('tenkan')
                    ichi = Indicator.get_ichimoku(data)
                    data['tenkan'] = ichi['TENKAN']
                    data['kijun'] = ichi['KIJUN']
                    data['senkou_span_a'] = ichi['senkou_span_a']
                    data['senkou_span_b'] = ichi['SENKOU']
                    data['chikou'] = ichi['CHIKOU']
                if 'apz' in self.indicator_list or self.all_indicators:
                    i_list.append('apz')
                    apz = Indicator.get_apz(data)
                    data['apz_up'] = apz['UPPER']
                    data['apz_low'] = apz['LOWER']
                if 'squeeze' in self.indicator_list or self.all_indicators:
                    i_list.append('squeeze')
                    data['squeeze'] = Indicator.get_squeeze(data)
                if 'vpt' in self.indicator_list or self.all_indicators:
                    i_list.append('vpt')
                    data['vpt'] = Indicator.get_vpt(data)
                if 'fve' in self.indicator_list or self.all_indicators:
                    i_list.append('fve')
                    data['fve'] = Indicator.get_fve(data)
                if 'vfi' in self.indicator_list or self.all_indicators:
                    i_list.append('vfi')
                    data['vfi'] = Indicator.get_fve(data)
                if 'msd' in self.indicator_list or self.all_indicators:
                    i_list.append('msd')
                    data['msd'] = Indicator.get_msd(data)

                if self.indicator_list is None or len(self.indicator_list) < 1:
                    self.indicator_list = list(data.columns)

            except IndicatorException:
                print('[?] Failed to grab one or more indicator for {}'.format(ticker))

        data = data.dropna(axis='columns', thresh=20)
        data = data.dropna(axis=0, how='any')
        return data


class IndicatorValidationException(IndicatorException):
    pass
