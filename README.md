## u-nectix

An algorithmic trading bot and backtesting framework. 

The name comes from a combination of the word "equity" and the animal genus [eunectes](https://en.wikipedia.org/wiki/Eunectes), because naming Python applications after snakes is fun. Given that this trading bot was built with the [Alpaca](https://alpaca.markets/) exchange in mind, a South American snake populating roughly the same geograhical vicinity as the alpaca made sense. 

Work is being done to implement cryptocurrency trading with [Kraken](https://www.kraken.com) with work also planned to implement forex trading with [Oanda](https://www.oanda.com). On March 11, 2020, I received an email from Kraken stating that limited forex pairs were now available to trade on their exchange, however they have not implemented forex for US customers yet. Their decision to do so may impact the forex implementation.

## algorithms currently implemented or WIP

  bullish_gainers_and_losers
  
  bullish_macd_crossover
  
  bullish_overnight_momentum
  
  efficient_frontier
  
  passive

## instructions

1. Clone repository

    `git clone https://github.com/bbeale/u-nectix.git`

    `cd u-nectix`

2. Install dependencies

    `pip install -r requirements.txt`

3. Add values to `config.ini`
   
   API keys for 
    - exchanges 
    - data sources
    
   For more details, see `config.ini.example` 

## run the script

    `python main.py -b -tp 60 -a passive`   
