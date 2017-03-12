from view import View
from model import Model


class Controller:
    def __init__(self, _view_, _model):
        self.view = _view_
        self.model = _model
        self.actions = {'1': self.scan,
                        '2': self.scan_social,
                        '0': self.exit_program
                        }

    def scan(self):
        self.view.output(self.model.scan_dnsmap(
            self.view.inp('Please input an IP or Domain name that you want to scan.\n')))

    def scan_social(self):
        self.model.scan_social(self.view.inp('Please input person initials.\n'))

    def exit_program(self):
        self.view.output('Program is closed. Have a nice day!')
        exit()

    def session(self):
        self.view.output('This is single host scanner and vk scanner.\n')
        while True:
            command = self.view.inp('What do you want to do?\n'
                                    '1 - Scan\n'
                                    '2 - Scan social\n'
                                    '0 - Exit\n')
            self.do_actions(command)

    def do_actions(self, command):
        try:
            self.actions[command]()
        except Exception as e:
            # raise e # debug
            return self.view.output('Wrong command: {}'.format(e))

if __name__ == '__main__':
    controller = Controller(View(), Model())
    controller.session()
