from cmd import Cmd
import getpass
from controller.controller_main import ControllerMain

controller = ControllerMain()


class CliHandler(Cmd):
    def do_exit(self, inp):
        print('Bye {} !!!'.format(getpass.getuser()))
        exit()

    def do_update(self, inp):
        controller.process(inp, 'update_table')

    def do_drop(self, inp):
        controller.process(inp, 'drop_table')

    def do_create(self, inp):
        controller.process(inp, 'create_table')
