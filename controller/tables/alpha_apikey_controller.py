from models.alpha_apikey import AlphaApiKey
from db.database import atomic_insert
import json
import time
from datetime import datetime


class AlphaApiKeyController():
    def __init__(self):
        self.process_switcher = {
            "update_table": self.update_table,
            "drop_table": self.drop_table,
            "create_table": self.create_table,
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
        AlphaApiKey.create_table()

    def drop_table(self):
        try:
            AlphaApiKey.drop_table()
        except Exception as err:
            print('drop table failed due to exception: '+str(err))

    def update_table(self):
        if not AlphaApiKey.table_exists():
            print('AlphaApiKey table not found')
            return
        file_path = input("file path(/home/user/Desktop/file.json): ")

        # test code need to be removed
        if file_path == 'test':
            print(datetime.now())
            for i in range(0, 35):
                AlphaApiKey.get_apikey()
                time.sleep(2)
            print(datetime.now())
            return

        try:
            with open(file_path) as json_file:
                data = json.load(json_file)
                print(data)
                atomic_insert(AlphaApiKey, data)
        except FileNotFoundError:
            print('{} file not found..'.format(file_path))
