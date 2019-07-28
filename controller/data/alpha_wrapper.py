import requests
import datetime
import time
from datetime import timedelta
from models.alpha_apikey import AlphaApiKey
from utils.pretty_json import *
from utils.proxy import *


class AlphaWrapper():
    def __init__(self):
        self.next_hit_time = datetime.datetime.now()
        self.base_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={sym}&interval=5min&apikey={key}&outputsize={size}'

    def sleep_if_required(self):
        if datetime.datetime.now() > self.next_hit_time:
            return
        else:
            time_delta = self.next_hit_time - datetime.datetime.now()
            time.sleep(time_delta.seconds)

    def get_ticker_data(self, symbol, compact):
        self.sleep_if_required()
        symbol = self.format_symbol(symbol)
        apikey = AlphaApiKey.get_apikey()
        op_size = 'compact' if compact else 'full'
        url = self.base_url.format(sym=symbol, key=apikey, size=op_size)
        response = None
        try:
            self.next_hit_time = datetime.datetime.now() + timedelta(seconds=13)
            response = requests.get(url)
            response = self.parse_response(response)
            response = self.parse_data(response)
        except requests.exceptions.HTTPError as err:
            print('Exception occurred: {}'.format(err))
        except Exception as err:
            print('Unhandled exception occured: {}'.format(err))
        return response

    def format_symbol(self, symbol):
        return '{}.NS'.format(symbol)

    def parse_response(self, response):
        try:
            http_status = response.status_code
            if http_status >= 200 and http_status < 300:
                response_body = response.json()
                response = response_body
        except Exception as err:
            print('Exception occured: '+str(err))
        return response

    def parse_data(self, response_data):
        try:
            response_data = response_data['Time Series (5min)']
        except KeyError as err:
            print('Response data: ')
            print_json(response_data)
            print('Exception(KeyError) from alpha api. err: '+str(err))
        except Exception as err:
            print('Unexpected data in response. err: '+str(err))
        return response_data
