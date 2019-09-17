from statistics import mean
from datetime import date, timedelta
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.sectorperformance import SectorPerformances
from alpha_vantage.techindicators import TechIndicators
import alpaca_trade_api as tradeapi
import configparser
import pprint
import sys
import time
import os

config = configparser.ConfigParser()

try:
    config.read(os.path.relpath("config.ini"))
except FileExistsError as e:
    print("FileExistsError: {}".format(e))
    sys.exit(1)

pp = pprint.PrettyPrinter()

api = tradeapi.REST(
    base_url    = config["alpaca"]["APCA_API_BASE_URL"],
    key_id      = config["alpaca"]["APCA_API_KEY_ID"],
    secret_key  = config["alpaca"]["APCA_API_SECRET_KEY"],
    api_version = config["alpaca"]["VERSION"]
)


def get_stuff_to_trade():
    """ Loops through all securities with volume data, grabs the best ones for trading according to the indicators

    :return vol_assets: list of dictionaries representing intraday, MACD, RSI, RoC, and stochastic oscillators
    """
    account                 = api.get_account()
    print("Account #:       {}".format(account.account_number))
    print("Currency:        {}".format(account.currency))
    print("Cash value:      ${}".format(account.cash))
    print("Buying power:    ${}".format(account.buying_power))

    print("DT count:        {}".format(account.daytrade_count))
    print("DT buying power: ${}".format(account.daytrading_buying_power))

    # Check if our account is restricted from trading.
    if account.trading_blocked:
        print("Account is currently restricted from trading.")

    # Check how much money we can use to open new positions.
    print("${} is available as buying power.".format(account.buying_power))

    active_assets = api.list_assets(status="active")

    # Filter the assets down to just those on NASDAQ.
    nasdaq_assets = [a for a in active_assets if a.exchange == "NASDAQ"]
    vol_assets = []
    for i in list(filter(lambda ass: ass.tradable is True, nasdaq_assets)):

        symbol = i.symbol
        today = date.fromtimestamp(time.time()).strftime("%Y-%m-%dT09:30:00-04:00")
        start = date.fromtimestamp(time.time() - 604800).strftime("%Y-%m-%dT09:30:00-04:00")
        barset = api.get_barset(symbol, "1Min", start=start, end=today)
        symbol_bars = barset[symbol]

        # Get trading volume
        volume = [bar.v for bar in symbol_bars if bar is not None]

        # And closing price
        closeprices = [bar.c for bar in symbol_bars if bar is not None]
        if volume is None:
            continue

        else:

            print("Symbol: ", symbol)
            # barset = api.get_barset(symbol[0], "15Min", after="2019-09-12T07:00:00-04:00")
            # asset = api.get_asset(symbol[0])
            # symbol_bars = barset[symbol[0]]

            alfavantage = TimeSeries(key=config["alpha_vantage"]["API_KEY"], output_format="pandas")
            indicators = TechIndicators(key=config["alpha_vantage"]["API_KEY"], output_format="pandas")

            tradedata = dict()
            tradedata["symbol"] = symbol
            # Get current ticker price
            tradedata["close"] = closeprices[0]
            # Get json object with the intraday data and another with  the call's metadata
            intraday, i_meta = alfavantage.get_intraday(symbol, interval="1min")
            tradedata["intraday"] = intraday['4. close']
            # Get the MACD
            macd, macd_meta = indicators.get_macd(symbol, interval="1min")
            tradedata["macd"] = macd["MACD"]
            # Get the RSI
            rsi, rsi_meta = indicators.get_rsi(symbol, interval="1min", time_period=100)
            tradedata["rsi"] = rsi["RSI"]
            # Get the RoC
            roc, roc_meta = indicators.get_roc(symbol, interval="1min", time_period=100)
            tradedata["roc"] = roc["ROC"]
            # Get stochastic oscillator
            stoc, stoc_meta = indicators.get_stoch(symbol, interval="1min")
            tradedata["stoc"] = stoc
            # And finally, calculate the limit
            limit_price = closeprices[0] - closeprices[0] * .1
            tradedata["limit"] = limit_price

            if len(volume) > 0:
                vmean = mean(volume)
                tradedata["vmean"] = vmean
                vol_assets.append(tradedata)
                # vol_assets.append((symbol, vmean, closeprices))

        if len(vol_assets) > 3:
            break
    return vol_assets


def find_best_security(asset_list):

    symbol = sorted(asset_list, key=lambda ass: ass["vmean"], reverse=True)[0]
    print("Symbol: ", symbol)

    # https://www.lazyfa.com/



    # TODO: Figure out what else I need to do with the data before trading it

    # Also, might want a better tech indicator lib that won't throttle me
    # https://www.worldtradingdata.com/pricing
    # https://daytradingz.com/trade-ideas/
    # https://daytradingz.com/gap-and-go-strategy/
    # https://daytradingz.com/low-float-stocks/
    # https://iextrading.com/developer/





    # barset = api.get_barset(symbol[0], "15Min", after="2019-09-12T07:00:00-04:00")
    # asset = api.get_asset(symbol[0])
    # symbol_bars = barset[symbol[0]]

    # alfavantage = TimeSeries(key=config["alpha_vantage"]["API_KEY"], output_format="pandas")
    # indicators = TechIndicators(key=config["alpha_vantage"]["API_KEY"], output_format="pandas")

    # tradedata = dict()
    # tradedata["symbol"] = symbol[0]
    # # Get current ticker price
    # tradedata["close"] = symbol[2][0]
    # # Get json object with the intraday data and another with  the call's metadata
    # intraday, i_meta = alfavantage.get_intraday(symbol[0], interval="1min")
    # tradedata["intraday"] = intraday['4. close']
    # # Get the MACD
    # macd, macd_meta = indicators.get_macd(symbol[0], interval="1min")
    # tradedata["macd"] = macd["MACD"]
    # # Get the RSI
    # rsi, rsi_meta = indicators.get_rsi(symbol[0], interval="1min", time_period=100)
    # tradedata["rsi"] = rsi["RSI"]
    # # Get the RoC
    # roc, roc_meta = indicators.get_roc(symbol[0], interval="1min", time_period=100)
    # tradedata["roc"] = roc["ROC"]
    # # Get stochastic oscillator
    # stoc, stoc_meta = indicators.get_stoch(symbol[0], interval="1min")
    # tradedata["stoc"] = stoc
    # # And finally, calculate the limit
    # limit_price = symbol[2][0] - symbol[2][0] * .1
    # tradedata["limit"] = limit_price

    return symbol


if __name__ == "__main__":
    get_stuff_to_trade()
