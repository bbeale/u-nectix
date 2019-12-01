# u-nectix

A WIP algorithmic trading bot written in Python that leverages traditional technical indicators, Twitter data, the EDGAR database of SEC filings, along with various machine learning models.

The name comes from a combination of the word "equity" and the animal genus [eunectes](https://en.wikipedia.org/wiki/Eunectes), because naming Python applications after snakes is fun. Given that this trading bot runs on the [Alpaca](https://alpaca.markets/) exchange, a South American snake populating roughly the same geograhical vicinity as the alpaca made sense.

# Instructions

Clone repository

`mkdir u-nectix && cd u-nectix`

`git clone https://github.com/bbeale/u-nectix`

Install dependencies

`pip install -r requirements.txt`

Add values to `config.ini`

Run the script

`python u-nectix.py`   


# Plans
- Add bearish / sell signal methods.
- Implement LSTM in `Predictor`.
- Implement buy/sell signals using `Predictor` outputs in `algos/` files.