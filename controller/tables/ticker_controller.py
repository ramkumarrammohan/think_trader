from models.script import Script
from models.ticker_5min import Ticker5min
import peewee


class TickerController():
    def __init__(self, data_controller):
        self.data_controller = data_controller
        self.process_switcher = {
            "update_table": self.update_table,
            "drop_table": self.drop_table,
            "create_table": self.create_table
        }

    def switcher_error(self, operation):
        print("Unhandled case operation: {} found".format(operation))

    def process(self, input):
        func = self.process_switcher.get(input, None)
        if func:
            func()
        else:
            self.switcher_error(input)

    def create_table(self):
        Ticker5min.create_table()

    def drop_table(self):
        Ticker5min.drop_table()

    def update_table(self):
        print('update table ticker_5min')
