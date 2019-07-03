from nsetools import Nse
from io import StringIO
import requests
import csv

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
        self.nifty500_list_url = 'https://www.nseindia.com/content/indices/ind_nifty500list.csv'
        self.driver = Nse()
        print(self.driver)

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

    def get_nifty_500_scripts(self):
        data = []
        try:
            response = requests.get(self.nifty500_list_url)
            csvfile = csv.reader(StringIO(response
                                          .content.decode('utf-8')), delimiter=',')
            for line in csvfile:
                d = {'symbol': line[2], 'company_name': line[0]}
                data.append(d)
            # Since first line of the csv is the header, removing that line
            data.pop(0)
        except Exception as err:
            print('Exception occured. err: '+str(err))
        return data
