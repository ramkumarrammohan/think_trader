from models.script import Script
from models.ticker_5min import Ticker5min
from models.alpha_apikey import AlphaApiKey
from utils.zonal_datetime import *
from utils.pretty_json import *
from db.database import atomic_insert
from datetime import date
from datetime import timedelta
from datetime import datetime
import peewee
import json

# global members
AlphaOpenPriceKey = '1. open'
AlphaHighPriceKey = '2. high'
AlphaLowPriceKey = '3. low'
AlphaClosePriceKey = '4. close'
AlphaVolumeKey = '5. volume'

ModelScriptIdKey = 'script_id'
ModelOpenPriceKey = 'open_price'
ModelHighPriceKey = 'high_price'
ModelLowPriceKey = 'low_price'
ModelClosePriceKey = 'close_price'
ModelVolumeKey = 'volume'
ModelRecordDateTimeKey = 'record_datetime'


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
        if not Ticker5min.table_exists():
            print('Ticker5min table not found')
            return

        expected_dt = self.get_expected_last_record_datettime()
        # get all scripts
        scripts = Script.select(Script.id, Script.symbol,
                                Script.company_name).where(Script.alpha_support == True)
        # Iterate through scripts and update the ticker data for each script
        for script in scripts:
            print('{}. {}'.format(script.id, script.symbol))
            last_ticker_data = (Ticker5min.select().where(
                                Ticker5min.script_id == script.id).order_by(
                                Ticker5min.record_datetime.desc())
                                ).limit(1)
            data = []
            if last_ticker_data:  # check for period that remaining data to be fetched
                last_updated_at = last_ticker_data[0].record_datetime
                if last_updated_at == expected_dt:
                    print('{} already upto date'.format(script.symbol))
                    continue
                elif last_updated_at > expected_dt:
                    print('{} is having future candle info. Ideally this is not possible. Please report this as bug'
                          .format(script.company_name))
                    continue
                else:
                    days_diff = expected_dt - last_updated_at
                    compact_response = True
                    if days_diff.days > 1:
                        compact_response = False
                    data = self.get_ticker_data(last_updated_at,
                                                script.id, script.symbol, compact_response)
            else:  # no ticker available for the script so get full data and insert
                older_datetime = datetime.strptime('2000 Jan 01 00:00:00',
                                                   DATE_TIME_FORMAT)
                data = self.get_ticker_data(older_datetime, script.id,
                                            script.symbol, False)
            if len(data):
                self.ticker_bulk_insert(data)

    def get_ticker_data(self, last_updated_at, script_id, symbol, compact):
        data = self.data_controller.get_ticker_data(symbol, compact)
        data_source = []
        for key, value in data.items():
            try:
                converted_dict = {}
                ist = ist_from_uscentral(key)

                if ist <= last_updated_at:
                    continue
                converted_dict[ModelScriptIdKey] = script_id
                converted_dict[ModelRecordDateTimeKey] = ist
                converted_dict[ModelOpenPriceKey] = value[AlphaOpenPriceKey]
                converted_dict[ModelHighPriceKey] = value[AlphaHighPriceKey]
                converted_dict[ModelLowPriceKey] = value[AlphaLowPriceKey]
                converted_dict[ModelClosePriceKey] = value[AlphaClosePriceKey]
                converted_dict[ModelVolumeKey] = value[AlphaVolumeKey]
                # magic no '0' - used to order by candle datetime
                data_source.insert(0, converted_dict)
            except Exception as err:
                print('Exception occured. err'+str(err))
        return data_source

    def ticker_bulk_insert(self, data):
        try:
            atomic_insert(Ticker5min, data)
        except Exception as err:
            print('Failed to insert records due to exception: '+str(err))

    def get_expected_last_record_datettime(self):
        """ returns the last candle datetime of the last market day
        return: datettime obj
        """
        expected_dt = datetime.now()
        weekday = expected_dt.date().isoweekday()
        if weekday > 5:  # (1, .., 5, 6, 7) == (mon, .., fri, sat, sun)
            days_to_subtract = weekday - 5
            expected_dt = expected_dt - timedelta(days=days_to_subtract)
        expected_dt = expected_dt.replace(
            hour=15, minute=25, second=00, microsecond=0)
        return expected_dt
