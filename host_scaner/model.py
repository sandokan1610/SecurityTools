import socket
import os
import re
import time

import nmap

from view import View
from data_manager import DataManager


class Model:
    def __init__(self):
        self.view = View()
        self.dm = DataManager()
        self.scanner = nmap.PortScanner()

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
            self.view.output('Scanning for subdomains...')
            st = time.time()
            os.system('dnsmap {} >> dnsmap.txt'.format(host))
            with open('dnsmap.txt') as f:
                dnsmap_scan = f.read()
            os.remove('dnsmap.txt')
            self.view.output(dnsmap_scan)
            subdomains = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", dnsmap_scan)
            if '127.0.0.1' in subdomains:
                del subdomains[subdomains.index('127.0.0.1')]
            self.view.output('Scanning founded subdomains...')
            for inx, subdomain in enumerate(subdomains, 1):
                self.scanner.scan(subdomain, '22-443', "-sV -O -A")
                self.dm.save_csv(self.scanner, subdomain)
                self.view.output('{}% completed...'.format(round(inx/len(subdomains)*100)))
            return 'completion time: {} second(s)'.format(round(time.time() - st, 2))
