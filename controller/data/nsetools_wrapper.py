from nsetools import Nse

LTPKey = 'lastPrice'
OpenPriceKey = 'open'
HighPricekey = 'dayHigh'
LowPriceKey = 'dayLow'
ClosePriceKey = 'closePrice'
Low52PriceKey = 'low52'
High52PriceKey = 'high52'
VolumeKey = 'totalTradedVolume'


class NseWrapper():
    def __init__(self):
        self.driver = Nse()
        print(self.driver)

    def get_all_scripts(self):
        data = []
        try:
            stock_codes = self.driver.get_stock_codes(cached=False)
            for key, value in stock_codes.items():
                data.append({
                    'symbol': str(key).upper(),
                    'company_name': value
                })
        except Exception as err:
            print('Exception araised(@get_all_scripts): '+err)
        return data

    def get_quote(self, symbol):
        data = None
        try:
            quote = self.driver.get_quote(symbol)
            data = {}
            data['ltp'] = quote[LTPKey]
            data['volume'] = quote[VolumeKey]
            data['day_open'] = quote[OpenPriceKey]
            data['day_high'] = quote[HighPricekey]
            data['day_low'] = quote[LowPriceKey]
            data['day_close'] = quote[ClosePriceKey]
            data['low_52'] = quote[Low52PriceKey]
            data['high_52'] = quote[High52PriceKey]
        except Exception as err:
            print('Exception araised(@get_quote): '+str(err))
        return data
