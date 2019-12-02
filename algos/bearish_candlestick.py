#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.asset_selector import AssetSelector
from src.indicators import Indicators
from util import submit_order, time_formatter
import time

def run(alpaca_api):

    # initial trade state
    trading_symbol  = None
    trading         = False
    assets          = AssetSelector(alpaca_api, edgar_token=None).bearish_candlesticks(64, 1)
    indicators      = Indicators(alpaca_api, assets).get_all_asset_indicators(backdate=time_formatter(time.time() - (604800 * 54)))

    # trade decision here
    for i in indicators.keys():

        instrument = indicators[i]
        # check the most recent moving average convergence-divergence
        # has the MACD crossed back down over its signal and is the MACD percentage change is negative?

        # TODO: factor out these bearish / sell signals and put them in asset_selector

        if instrument["macd"].iloc[-1] < instrument["signal"].iloc[-1] and instrument["macd_ptc"].iloc[-1] < 0:
            # if the MACD checks out, check the directional movement indicator
            # has the DMI negative value crossed over the positive value? Is percentage change positive?
            if instrument["DMp"].iloc[-1] < instrument["DMm"].iloc[-1] and instrument["DMm_ptc"].iloc[-1] < 0:
                # if DMI checks out, check the volume zone oscillator
                # the VZO should cross into the bullish range and continue going up
                if (instrument["vzo"].iloc[-3] < instrument["vzo"].iloc[-2] < -40 < instrument["vzo"].iloc[-1]) and \
                        instrument["vzo_ptc"].iloc[-1] > 0:
                    trading = True
                    trading_symbol = str(i)

                elif (instrument["vzo"].iloc[-2] < -40 < instrument["vzo"].iloc[-1]) and \
                        instrument["vzo_ptc"].iloc[-1] > 0:
                    trading = True
                    trading_symbol = str(i)

        if trading_symbol is not None:
            break

    # debugging line that forces the trade to not be made
    print("Trading: ", trading is True)
    trading = False
    if trading is True:
        # decide how much to buy # TODO
        quant = 10

        # then submit a sell order
        submit_order(
            api_reference=alpaca_api,
            ticker=trading_symbol,
            qty=quant,
            transaction_side="sell",
            ttype="market",
            time_in_force="ioc"
        )
