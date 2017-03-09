import nmap
import socket

from host_scaner.view import View
from host_scaner.data_manager import DataManager


class Model:
    def __init__(self):
        self.view = View()
        self.dm = DataManager()
        self.nm = nmap.PortScanner()

    @staticmethod
    def check_host(host):
        try:
            socket.gethostbyname(host)
            return True
        except socket.gaierror:
            return False

    def scan(self, host):
        if not self.check_host(host):
            return 'Wrong host: "{}"'.format(host)
        else:
            self.view.output('Scanning...')
            self.nm.scan(host)
            return self.dm.save_csv(self.nm.csv())
