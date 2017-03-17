import time

import nmap

from view import output
from .data_manager import DataManager


class ScannerNetwork:
    def __init__(self):
        self.dm = DataManager()
        self.scanner = nmap.PortScanner()

    def scan(self, network):
        output('Scanning network...')
        start = time.time()
        self.scanner.scan(network or '192.168.1.0/24', arguments='-O -T5')
        output('Completion time: {} second(s)'.format(round(time.time() - start, 2)))
        output(self.dm.save_csv(self.scanner, 'network'))
