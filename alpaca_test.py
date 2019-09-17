from statistics import mean
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.sectorperformance import SectorPerformances
from alpha_vantage.techindicators import TechIndicators
import alpaca_trade_api as tradeapi
import configparser
import pprint
import sys
import os


def get_stuff_to_trade():
    config = configparser.ConfigParser()

    try:
        config.read(os.path.relpath("config.ini"))
    except FileExistsError as e:
        print("FileExistsError: {}".format(e))
        sys.exit(1)

    pp = pprint.PrettyPrinter()

    api                     = tradeapi.REST(
        base_url    = config["alpaca"]["APCA_API_BASE_URL"],
        key_id      = config["alpaca"]["APCA_API_KEY_ID"],
        secret_key  = config["alpaca"]["APCA_API_SECRET_KEY"],
        api_version = config["alpaca"]["VERSION"]
    )

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
    for i in list(filter(lambda ass: ass.tradable == True, nasdaq_assets)):
        symbol = i.symbol

        barset = api.get_barset(symbol, "15Min", start="2019-09-01T09:30:00-04:00", end="2019-09-12T09:30:00-04:00")
        symbol_bars = barset[symbol]

        # get trading volume
        volume = [bar.v for bar in symbol_bars if bar is not None]
        if volume is None:
            continue

        else:
            if len(volume) > 0:
                vmean = mean(volume)
                vol_assets.append((symbol, vmean))

        if len(vol_assets) > 3:
            break

        # Submit a market order to buy 1 share of Apple at market price
        # api.submit_order(
        #     symbol="AAPL",
        #     qty=1,
        #     side="buy",
        #     type="market",
        #     time_in_force="gtc"
        # )

        # Submit a limit order to attempt to sell 1 share of AMD at a
        # particular price ($20.50) when the market opens
        # api.submit_order(
        #     symbol="AMD",
        #     qty=1,
        #     side="sell",
        #     type="limit",
        #     time_in_force="opg",
        #     limit_price=20.50
        # )

    symbol = sorted(vol_assets, key=lambda ass: ass[1], reverse=True)[0]
    print("Symbol: ", symbol)
    asset = api.get_asset(symbol[0])
    barset = api.get_barset(symbol[0], "15Min", after="2019-09-12T07:00:00-04:00")
    symbol_bars = barset[symbol[0]]

    alfavantage = TimeSeries(key=config["alpha_vantage"]["API_KEY"], output_format="pandas")
    indicators = TechIndicators(key=config["alpha_vantage"]["API_KEY"], output_format="pandas")

    tradedata = {}
    # Get json object with the intraday data and another with  the call's metadata
    intraday, i_meta_data = alfavantage.get_intraday(symbol[0], interval="60min")
    tradedata["intraday"] = intraday

    macd, macd_meta_data = indicators.get_macd(symbol[0], interval="daily")
    tradedata["macd"] = macd

    return tradedata


if __name__ == "__main__":
    get_stuff_to_trade()
