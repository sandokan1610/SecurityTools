from view import View
from model import Model


class Controller:
    def __init__(self, _view_, _model):
        self.view = _view_
        self.model = _model

    def session(self):
        self.view.output('This is single host scanner.\n')
        while True:
            host = self.view.inp('Please input an IP or Domain name that you want to scan.\n')
            self.view.output(self.model.scan(host))

if __name__ == '__main__':
    controller = Controller(View(), Model())
    controller.session()
