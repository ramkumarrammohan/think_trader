from controller.strategies.breakout_5min import Breakout5min


class StrategyController():
    def __init__(self):
        self.breakout_5min = Breakout5min()
        self.process_switcher = {
            "bt": self.breakout_5min.apply,
        }

    def switcher_error(self, operation):
        print("Unhandled case operation: {} not found".format(operation))

    def process(self, input):
        func = self.process_switcher.get(input, None)
        if func:
            func()
        else:
            self.switcher_error(input)
