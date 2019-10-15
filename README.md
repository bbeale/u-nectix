# cryptoconda

A WIP algorithmic trading bot written in Python that leverages traditional technical indicators (currently MACD, MFI and stochastic oscillators), Twitter data, the EDGAR database of SEC filings, and a simple regression algorithm implemented with Tensorflow.

The name "crypto" comes from the original intended trading instrument of this bot, which was going to be a simple rebuild of [tradeSnake](https://github.com/bbeale/tradeSnake) for trading cryptocurrencies. This was before I discovered the [Alpaca](https://alpaca.markets/) platform and decided that an investment instrument- and exchange-agnostic bot would be best. I previously ran tradeSnake on [Poloniex](https://poloniex.com/), so Poloniex integration makes sense for cryptoconda as well.

Basic default strategy (again, WIP, so more strategies are coming:
- Scan the list of tradeable securities for specific candlestick patterns. Add those securities to a collection of bullish or bearish patterns, return the first of those collections to reach a certain number of securities. This will be the bucket to pick from. 
- For each of those bullish patterns, check for a MACD buy signal.
- If the security has an affirmative MACD buy signal, calculate the other indicators.

(in progress/planning):
- If the other indicators point more to "yes" than "no", establish a long position.
- Add corresponding checks and signals for bearish patterns and short positions.


# Instructions

Clone repository

`mkdir cryptoconda && cd cryptoconda`

`git clone https://github.com/bbeale/cryptoconda`

Install dependencies

`pip install -r requirements.txt`

Add values to `config.ini`

Run the script

`python cryptoconda.py`   


# Plans
- Generate trading signal from `Predictor` class outputs
- Look into why `EdgarInterface.calculate_edgar_signal()` is failing for some 8-K forms
- Look into a better ML implementation
- Cryptocurrency exchange interface (Poloniex? Robinhood?)
