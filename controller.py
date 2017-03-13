from view import View
from model import Model


class Controller:
    def __init__(self, _view_, _model):
        self.view = _view_
        self.model = _model
        self.actions = {'1': self.scan_remote_host,
                        '2': self.scan_network,
                        '3': self.scan_social,
                        '4': self.scan_sql,
                        '0': self.exit_program
                        }

        self.db_sql = {'1': self.scan_mysql,
                       #'2': self.scan_mssql,
                       #'3': self.scan_oracle,
                       #'4': self.scan_all_sql,
                       '0': self.session
                       }

    def scan_remote_host(self):
        self.view.output(self.model.scan_remote_host(
            self.view.inp('Please input an IP or Domain name that you want to scan.\n')))

    def scan_network(self):
        self.view.output(self.model.scan_network(
            self.view.inp('Please input network that you want to scan or leave empty for 192.168.1.0/24.\n')))

    def scan_social(self):
        self.model.scan_social(self.view.inp('Please input person initials.\n'))

    def scan_sql(self):
        command = self.view.inp('What db do you want to scan?\n'
                                '1 - MySQL\n'
                                '2 - MSSQL\n'
                                '3 - Oracle\n'
                                '0 - Back\n')
        self.do_actions(command, 'sql')
        self.session()

    def contact_elements(self):
        first_name = self.view.inp('Insert first name\n')
        last_name = self.view.inp('Insert last name\n')
        phone_number = self.view.inp('Insert phone number\n')
        return first_name, last_name, phone_number

    def scan_mysql(self):
        self.model.scan_mysql(*self.contact_elements())

    def exit_program(self):
        self.view.output('Program is closed. Have a nice day!')
        exit()

    def session(self):
        self.view.output('This is single host scanner and vk scanner.\n')
        while True:
            command = self.view.inp('What do you want to do?\n'
                                    '1 - Scan remote host\n'
                                    '2 - Scan network\n'
                                    '3 - Scan social\n'
                                    '4 - Scan databases\n'
                                    '0 - Exit\n')
            self.do_actions(command)

    def do_actions(self, command, choose=''):
        try:
            if choose == 'sql':
                self.db_sql[command]()
            else:
                self.actions[command]()
        except Exception as e:
            # raise e # debug
            return self.view.output('Wrong command: {}'.format(e))


if __name__ == '__main__':
    controller = Controller(View(), Model())
    controller.session()
