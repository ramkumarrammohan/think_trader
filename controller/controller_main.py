from .tables.script_controller import ScriptController
from .tables.script_info_controller import ScriptInfoController
from .tables.ticker_controller import TickerController
from .data.data_controller import DataController


class ControllerMain():
    def __init__(self):
        self.data_controller = DataController()
        self.script_controller = ScriptController(self.data_controller)
        self.script_info_controller = ScriptInfoController(
            self.data_controller)
        self.ticker_controller = TickerController(self.data_controller)
        self.process_switcher = {
            "script": self.script_controller.process,
            "script_info": self.script_info_controller.process,
            "ticker_5min": self.ticker_controller.process
        }

    def switcher_error(self, table, operation):
        print("Unhandled case for table:{}, operation: {}".format(table, operation))

    def process(self, table, operation):
        func = self.process_switcher.get(table, None)
        if func:
            func(operation)
        else:
            self.switcher_error(table, operation)
