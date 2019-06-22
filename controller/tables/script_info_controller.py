from models.script import Script
from models.script_info import ScriptInfo
import peewee


class ScriptInfoController():
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
        ScriptInfo.create_table()

    def drop_table(self):
        ScriptInfo.drop_table()

    def update_table(self):
        if not ScriptInfo.table_exists():
            print('ScriptInfo table not found')
            return
        # get all scripts
        scripts = Script.select(Script.id, Script.symbol,
                                Script.company_name)
        # get into from data_controller one by one & save into table
        for script in scripts:
            print('{}. {}'.format(script.id, script.symbol))
            data = self.data_controller.get_quote(script.symbol)
            if data:
                data['script_id'] = script.id
                # Note: below operation leads to change in primary_key(autoincr id)
                # check for any other way without change in autoincr_id update
                ScriptInfo.insert(**data).on_conflict('replace').execute()
            else:
                print('Failed to update {}'.format(script.company_name))
