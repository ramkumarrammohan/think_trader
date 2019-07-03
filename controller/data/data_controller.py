from .nsetools_wrapper import NseWrapper
from .alpha_wrapper import AlphaWrapper


class DataController():
    def __init__(self):
        self.nse_wrapper = NseWrapper()
        self.alpha_wrappper = AlphaWrapper()

    def get_active_scripts(self):
        return self.nse_wrapper.get_nifty_500_scripts()

    def get_quote(self, symbol):
        return self.nse_wrapper.get_quote(symbol)

    def get_ticker_data(self, symbol, compact):
        """ used to get ticker(5min) data
        Arguments:
            symbol(string) - script symbol
            mode: true/false.
            true - full data
            false - compact data
        Returns:
            dict data
        """
        return self.alpha_wrappper.get_ticker_data(symbol, compact)
