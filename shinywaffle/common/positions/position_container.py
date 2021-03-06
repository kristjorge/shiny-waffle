from shinywaffle.common.context import Context


class PositionContainer:

    """
    Positions are closed FIFO
    """

    def __init__(self, context: Context):
        self.active_positions = {asset: [] for asset in context.assets.keys()}
        self.exited_positions = {asset: [] for asset in context.assets.keys()}
        self.account = context.account
        self.context = context
        self.latest_active_id = 0

    def enter_position(self, p):
        self.active_positions[p.asset.ticker].append(p)
        self.active_positions[p.asset.ticker][-1].id = self.latest_active_id
        self.latest_active_id += 1

    def sell_off_position(self, ticker, volume, price, time):

        """
        Method that sells of "size" amount of the oldest position of asset "ticker" at the price "price" at the
        timestamp "timestamp"

        :param ticker: Ticker of the asset that is being sold
        :param volume: The order volume
        :param price: The order price
        :param time: The timestamp
        """

        remaining_volume = volume
        while remaining_volume > 0:
            is_active, filled_volume, remaining_volume = self.active_positions[ticker][0].sell_off(remaining_volume,
                                                                                                   price,
                                                                                                   time)
            if not is_active:
                self.exited_positions[ticker].append(self.active_positions[ticker].pop(0))

    def update_positions(self):
        for p in self.iter_active():
            p.update(self.context.retrieved_data)

    def report(self):
        data = {}
        for p in self.iter_active():
            data[p.id] = p.report()
        for p in self.iter_exited():
            data[p.id] = p.report()
        return data

    def iter_active(self):
        for ticker in self.active_positions.keys():
            for p in self.active_positions[ticker]:
                yield p

    def iter_exited(self):
        for ticker in self.exited_positions.keys():
            for p in self.exited_positions[ticker]:
                yield p
