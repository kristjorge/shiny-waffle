from data.time_series_data import TimeSeries
from backtesting.stock.stops import TrailingStop
from backtesting.stock.stops import StopLoss
from backtesting.stock.stops import TargetStop
from backtesting.stock.stops import StopHolder
from data.time_series_data import DataSeriesContainer
from tools.api_link import APILink
from strategy.strategy import TradingStrategy
from utils.misc import daily_datetime_format
from common.context import Context


class Asset:

    """
    Base class for tradable assets. Classes that inherit from assets are:
        - Stocks
        - Forex
        - Cryptocurrencies
    """

    def __init__(self, context: Context, name: str, ticker: str, base_currency: str):
        self.name = name
        self.ticker = ticker
        self.base_currency = base_currency
        self.datetime_format = daily_datetime_format
        self.bars = None
        self.data = DataSeriesContainer()
        self.stops = StopHolder()
        self.latest_bar = None
        context.assets[self.ticker] = self

    def set_bars(self, bars):
        assert isinstance(bars, TimeSeries) or isinstance(bars, APILink)
        self.bars = bars

    def add_data_series(self, name, data_series):

        """
        Method to add data series to the financial asset. Data series represent time series data like price data
        or sentiment data
        :param name: Name to be referenced
        :param data_series: DataSeries object
        """

        assert isinstance(data_series, TimeSeries)
        self.data.add(data_series, name)

    def set_stop(self, stop_object):
        if isinstance(stop_object, StopLoss):
            setattr(self.stops, "stop_loss", stop_object)
        elif isinstance(stop_object, TrailingStop):
            setattr(self.stops, "trailing_stop", stop_object)
        elif isinstance(stop_object, TargetStop):
            setattr(self.stops, "target_stop", stop_object)

    def self2dict(self):

        """
        Returning a serializable dictionary that can be reported in a json file by the reporter class
        :return: data (dictionary)
        """

        data = {
            'name': self.name,
            'ticker': self.ticker,
            'base_currency:': self.base_currency
        }
        return data


class Stock(Asset):

    def __init__(self, context, name, ticker, base_currency):
        super().__init__(context, name, ticker, base_currency)
        self.type = "stock"
        self.num_decimal_points = 0


class Forex(Asset):

    def __init__(self, context, name, ticker, base_currency):
        super().__init__(context, name, ticker, base_currency)
        self.type = "forex"
        self.num_decimal_points = 2


class Cryptocurrency(Asset):

    def __init__(self, context, name, ticker, base_currency):
        super().__init__(context, name, ticker, base_currency)
        self.type = "cryptocurrency"
        self.num_decimal_points = 8


class BaseAsset:
    def __init__(self, num_decimal_points):
        self.is_base_asset = True
        self.num_decimal_points = num_decimal_points


class USD(BaseAsset):
    def __init__(self):
        BaseAsset.__init__(self, 2)


class USDT(BaseAsset):
    def __init__(self):
        BaseAsset.__init__(self, 2)


class BTC(BaseAsset):
    def __init__(self):
        BaseAsset.__init__(self, 8)


class ETH(BaseAsset):
    def __init__(self):
        BaseAsset.__init__(self, 8)