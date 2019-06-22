from models.script import Script
from db.database import atomic_insert


class ScriptController():
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
        Script.create_table()

    def drop_table(self):
        try:
            Script.drop_table()
        except Exception as err:
            print('drop table failed due to exception: '+str(err))

    def update_table(self):
        if not Script.table_exists():
            print('Script table not found')
            return
        # get the list of scripts from data_controller & insert into script
        data = self.data_controller.get_active_scripts()
        # pop first item. Since, the first item in the list contains header of csv({'symbol': 'SYMBOL', 'company_name': 'NAME OF COMPANY'})
        data.pop(0)
        try:
            atomic_insert(Script, data)
        except Exception as err:
            print('Failed to insert records due to exception: '+str(err))
