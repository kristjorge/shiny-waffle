from datetime import datetime

from shinywaffle.data.bar_provider import BarProvider
from shinywaffle.backtesting.backtest import Backtester
from shinywaffle.risk.risk_management import BaseRiskManager
from shinywaffle.common.assets import assets
from shinywaffle.common.account import Account
from shinywaffle.backtesting.broker import BacktestBroker
from shinywaffle.strategy import sma_crossover
from shinywaffle.common.context import Context


context = Context()

broker = BacktestBroker(context, 0.)
trading_strategy = sma_crossover.AverageCrossOver(context=context, short=15, long=40)

# Nvidia stocks
nvidia = assets.Stock(context, "Nvidia", "NVDA", assets.USD())
nvidia_bars = BarProvider('D:/PythonProjects/shiny-waffle/shinywaffle/data/yahoo_finance/NVDA_1D.csv', '%Y-%m-%d')
nvidia.set_bars(nvidia_bars)

# Oracle stocks
oracle = assets.Stock(context, "Oracle", "ORCL", assets.USD())
oracle_bars = BarProvider('D:/PythonProjects/shiny-waffle/shinywaffle/data/yahoo_finance/ORCL_1D.csv', '%Y-%m-%d')
oracle.set_bars(oracle_bars)

# IBM stocks
ibm = assets.Stock(context, "IBM", "IBM", assets.USD())
ibm_bars = BarProvider('D:/PythonProjects/shiny-waffle/shinywaffle/data/yahoo_finance/IBM_1D.csv', '%Y-%m-%d')
ibm.set_bars(ibm_bars)

trading_strategy.apply_to_asset(nvidia, oracle, ibm)

risk_manager = BaseRiskManager(context)
account = Account(context, 1000, assets.USD())
backtester = Backtester(context, 'daily', run_from=datetime(2011, 1, 1), run_to=datetime(2020, 1, 1))
backtester.run()