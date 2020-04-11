from collections import namedtuple


class Position:

    # TODO: Store transaction commissions here too

    transaction = namedtuple("Transaction", ["volume", "price", "size", "timestamp"])

    def __init__(self, timestamp_opened, asset, volume, size, price):
        self.opened = timestamp_opened
        self.asset = asset
        self.id = None
        self.volume = volume
        self.volume_remaining = volume
        self.size = size
        self.enter_price = price
        self.partial_closed_amount = 0
        self.closed = None
        self.close_price = None
        self.is_active = True
        self.time_in_trade = 0
        self.time_series = {
            'value': [],
            'return': [],
            'return percentage': [],
            'times': [],
            'volume remaining': []
        }
        self.transactions = []

    def sell_off(self, volume, price, timestamp):
        """

        Method to partially close a position. Incrementing the partial return member variable by the order size.
        Decrements the self.remaining_volume member variable by the volume of the partial close
        If self.remaining_volume is then totalled to 0, calculate the average close price which triggers the
        final closure of the position

        :param volume: volume of the partial close
        :param price: Price at which the position was partially closed
        :param timestamp: Datetime object
        :return: is_closed flag indicating whether or not a position is fully closed out or not
        """
        # TODO: Fix issue where the volume is 2.99999996 instead of 3 (as an example) resulting in not closing out
        # position
        size = volume * price
        self.partial_closed_amount += size
        self.volume_remaining -= volume
        self.transactions.append(Position.transaction(volume, price, size, timestamp))

        if self.volume_remaining == 0:
            self.closed = timestamp
            self.close_price = sum([t.volume * t.price for t in self.transactions]) / sum([t.volume for t in self.transactions])
            self.is_active = False

        return self.is_active

    def update(self, time_series_data):

        """
        Method to update the position metrics each time a new time series data event is received received
        by the event handler
        :param time_series_data: Time series data object received by the data provider
        """
        close_price = time_series_data[self.asset.ticker]['bars'][0].close
        current_time = time_series_data['current time']
        remaining_value = self.volume_remaining * close_price

        self.time_series['value'].append(remaining_value + self.partial_closed_amount)
        self.time_series['return'].append(remaining_value + self.partial_closed_amount - self.volume * self.enter_price)
        self.time_series['return percentage'].append(self.time_series['return'][-1] / self.size)
        self.time_series['times'].append(current_time.strftime("%d-%m-%Y %H:%M:%S"))
        self.time_in_trade += (current_time - self.opened).days
        try:
            self.time_series['volume remaining'].append(self.time_series['volume remaining'][-1])
        except IndexError:
            self.time_series['volume remaining'].append(self.volume_remaining)

    def self2dict(self):
        data = {
            'id': self.id,
            'asset': self.asset.name,
            'opened': self.opened.strftime("%d-%m-%Y %H:%M:%S"),
            'volume': self.volume,
            'size': self.size,
            'enter price': self.enter_price,
            'volume weighted close price': self.close_price,

            'time series': {
                'value': self.time_series['value'],
                'return': self.time_series['return'],
                'return percentage': self.time_series['return percentage'],
                'time in trade': self.time_series['time in trade'],
                'times': self.time_series['times'],
                'volume remaining': self.time_series['volume remaining']
            }
        }

        try:
            data['closed'] = self.closed.strftime("%d-%m-%Y %H:%M:%S")
        except AttributeError:
            data['closed'] = "Position not closed"

        return data