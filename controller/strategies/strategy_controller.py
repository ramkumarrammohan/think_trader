from controller.strategies.breakout_5min import Breakout5min


class StrategyController():
    def __init__(self):
        self.breakout_5min = Breakout5min()
        print("strategy controller init")
        self.process_switcher = {
            "breakout_5min": self.breakout_5min.apply,
        }

    def switcher_error(self, operation):
        print("Unhandled case operation: {} found".format(operation))

    def process(self, input):
        func = self.process_switcher.get(input, None)
        if func:
            func()
        else:
            self.switcher_error(input)
