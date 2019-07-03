import requests


class AlphaWrapper():
    def __init__(self):
        self.base_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={sym}&interval=5min&apikey={key}&outputsize={size}'
        print('Alpha api driver')

    def get_ticker_data(self, symbol, compact):
        symbol = self.format_symbol(symbol)
        apikey = self.get_apikey()
        op_size = 'compact' if compact else 'full'
        url = self.base_url.format(sym=symbol, key=apikey, size=op_size)
        response = None
        try:
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

    def get_apikey(self):
        return 'IKS3X2GLUX2F7WOE'

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
            print('Exception(KeyError) from alpha api. err: '+str(err))
            print('Response data: '+response_data)
        except Exception as err:
            print('Unexpected data in response. err: '+str(err))
        return response_data
