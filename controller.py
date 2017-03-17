from view import output, inp
from scanner_remote_host.model import ScannerRemoteHost
from scanner_network.model import ScannerNetwork
from scanner_social.model import ScannerSocial
from scanner_databases.model import ScannerDatabase


class Controller:
    def __init__(self):
        self.scanner_remote_host = ScannerRemoteHost()
        self.scanner_network = ScannerNetwork()
        self.scanner_social = ScannerSocial()
        self.scanner_databases = ScannerDatabase()
        self.actions = {'1': self.run_scan_remote_host,
                        '2': self.run_scan_network,
                        '3': self.run_scan_social,
                        '4': self.run_scan_sql,
                        '0': self.exit_program
                        }

        self.db_sql = {'1': self.run_scan_mysql,
                       '2': self.run_scan_mssql,
                       '3': self.run_scan_postgresql,
                       '0': self.session
                       }

    def run_scan_remote_host(self):
        self.scanner_remote_host.scan(inp('Please input an IP or Domain name that you want to scan.\n'))

    def run_scan_network(self):
        self.scanner_network.scan(inp('Please input network that you want to scan '
                                      'or leave empty for 192.168.1.0/24.\n'))

    def run_scan_social(self):
        self.scanner_social.scan(inp('Please input person initials.\n'))

    def run_scan_sql(self):
        command = inp('What db do you want to scan?\n'
                      '1 - MySQL\n'
                      '2 - MSSQL\n'
                      '3 - PostgreSQL\n'
                      '0 - Back\n')
        self.do_actions(command, 'sql')
        self.session()

    @staticmethod
    def contact_elements():
        first_name = inp('Insert first name\n')
        last_name = inp('Insert last name\n')
        phone_number = inp('Insert phone number\n')
        return first_name, last_name, phone_number

    def run_scan_mysql(self):
        conn, cursor = self.scanner_databases.connect_mysql()
        output(self.scanner_databases.scan_mysql(conn, cursor, *self.contact_elements()))

    def run_scan_mssql(self):
        conn, cursor = self.scanner_databases.connect_mssql()
        output(self.scanner_databases.scan_mssql(conn, cursor, *self.contact_elements()))

    def run_scan_postgresql(self):
        conn, cursor = self.scanner_databases.connect_postgresql()
        output(self.scanner_databases.scan_postgresql(conn, cursor, *self.contact_elements()))

    @staticmethod
    def exit_program():
        output('Program is closed. Have a nice day!')
        exit()

    def session(self):
        output('This is remote host, social, network and database scanner.\n')
        while True:
            command = inp('What do you want to do?\n'
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
            return output('Error: {}'.format(e))


if __name__ == '__main__':
    controller = Controller()
    controller.session()
