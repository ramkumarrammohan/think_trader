from .nsetools_wrapper import NseWrapper


class DataController():
    def __init__(self):
        self.nsewrapper = NseWrapper()

    def get_active_scripts(self):
        return self.nsewrapper.get_all_scripts()

    def get_quote(self, symbol):
        return self.nsewrapper.get_quote(symbol)
