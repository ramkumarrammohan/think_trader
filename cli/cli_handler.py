from cmd import Cmd
import getpass

class CliHandler(Cmd):
    def do_exit(self, inp):
        print ('Bye {} !!!'.format(getpass.getuser()))
        exit()
    def do_update(self, inp):
        print ('Updating {}'.format(inp))
        # handle event to corresponding function