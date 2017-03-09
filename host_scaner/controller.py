from host_scaner.view import View
from host_scaner.model import Model


class Controller:
    def __init__(self, _view_, _model):
        self.view = _view_
        self.model = _model
        self.actions = {'1': self.scan}

    def scan(self):
        self.view.output(self.model.scan(self.view.inp('Please input an IP or Domain name that you want to scan.\n')))

    def session(self):
        self.view.output('This is single host scanner.\n')
        while True:
            command = self.view.inp('What do you want to do?\n1 - Scan\n')
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
