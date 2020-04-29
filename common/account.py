from datetime import datetime
from common.event import events
from backtesting.tradelog import TradeLog
from common.positions.position_container import PositionContainer
from common.positions.position import Position
from common.assets.assets import Asset
from common.context import Context


class Account:

    """

    Class holding the initial holding in a base currency for the backtesting

    """

    # TODO: Implement round down method

    def __init__(self, context: Context, initial_holding: float, currency: str, num_base_decimals: int = 2):
        self.initial_holding = initial_holding
        self.cash = initial_holding
        self.total_value = initial_holding
        self.base_currency = currency
        self.base_currency_decimals = num_base_decimals
        self.assets = {asset.ticker: {'holding': 0, 'value': 0, 'asset_data': asset} for asset in context.assets.values()}
        self.times = []
        self.time_series = {
            'total value': [],
            'cash': [],
            'number of active positions': []
        }
        self.trade_log = TradeLog()
        self.times_readable = []
        self.risk_manager = None
        self.positions = PositionContainer(context)
        context.account = self
        self.context = context

        try:
            self.risk_manager = context.risk_manager
        except AttributeError:
            print('Risk manager not provided in context...')

        try:
            context.risk_manager.account = self
        except AttributeError:
            print('Risk manager not provided in context...')

    def debit(self, amount: float):
        self.cash += amount

    def credit(self, amount: float):
        self.cash -= amount

    @ staticmethod
    def place_buy_order(asset: Asset, order_size: float, price: float = None) -> events.MarketOrderSellEvent or events.LimitOrderSellEvent:
        if price is None:
            event = events.MarketOrderBuyEvent(asset, order_size)
        else:
            event = events.LimitOrderBuyEvent(asset, order_size, price)
        return event

    def place_sell_order(self, asset: Asset, order_size: float, price: float = None):
        max_volume = self.assets[asset.ticker]['holding']
        if price is None:
            event = events.MarketOrderSellEvent(asset, order_size, max_volume)
        else:
            event = events.LimitOrderSellEvent(asset, order_size, price, max_volume)
        return event

    def register_order(self, event, timestamp: datetime):
        """
        Method to register a filled order from the broker on the account.
        This method logs a trade with the self.trade_log

        If the event.type == 'buy' then
                1) a new position in the position container is established
                2) Increment the holding for the respective asset
                3) Decrement the cash is decremented equal to the transaction amount
                4) Decrement the cash the amount for the commission

        IF the event.type == 'sell' then
                1) Call 'sell_off_position' from the position container
                2) Decrement the holding for the respective asset
                3) Increment the cash equal to the transaction amount
                4) Decrement the cash the amount for the commission
        :param event:
        :param timestamp:
        :return:
        """

        self.trade_log.new_trade(event.asset, event.order_size,
                                 event.price, event.order_volume,
                                 event.type, timestamp, event.commission)

        if event.type == 'buy':
            position = Position(timestamp, event.asset, event.order_volume,
                                event.order_size, event.price)

            self.positions.enter_position(position)
            self.assets[event.asset.ticker]['holding'] += event.order_volume
            self.credit(event.order_size)
            self.credit(event.commission)

        elif event.type == 'sell':
            self.positions.sell_off_position(event.asset.ticker, event.order_volume, event.price, timestamp)
            self.assets[event.asset.ticker]['holding'] -= event.order_volume
            self.debit(event.order_size)
            self.credit(event.commission)

    def update_portfolio(self):
        """
        Update various values for the account object:
            - Total value
            - Cash
            - Report times
            - Various position tracking functionalities
        :return:
        """
        total_value = self.cash
        for ticker, asset in self.assets.items():
            if ticker in self.context.retrieved_data.asset_data.keys():
                asset['asset_data'].latest_bar = self.context.retrieved_data.asset_data[ticker]['bars'][0]
                try:
                    asset['value'] = asset['holding'] * asset['asset_data'].latest_bar.close
                except TypeError:
                    # Catching None
                    asset['value'] = 0
                finally:
                    total_value += asset['value']

        self.times.append(self.context.retrieved_data.time)
        self.times_readable.append(self.context.retrieved_data.time.strftime('%d-%m-%Y %H:%M:%S'))
        self.total_value = total_value
        self.time_series['total value'].append(total_value)
        self.time_series['cash'].append(self.cash)
        self.time_series['number of active positions'].append(self.trade_log.active_trades)
        self.positions.update_positions()

    def self2dict(self):
        data = {
            'trades': self.trade_log.self2dict(),
            'times': self.times_readable,
            'total value': self.time_series['total value'],
            'cash': self.time_series['cash'],
            'active trades': self.time_series['number of active positions'],
            'positions': self.positions.report()
        }

        return data
