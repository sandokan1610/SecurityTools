import os
import re
import socket
import time

import nmap

from view import output
from .data_manager import DataManager


class ScannerRemoteHost:
    def __init__(self):
        self.dm = DataManager()
        self.scanner = nmap.PortScanner()
        if not os.path.exists('temp'):
            os.makedirs('temp')

    @staticmethod
    def check_host(host):
        try:
            socket.gethostbyname(host)
            return True
        except socket.gaierror:
            return False

    def scan(self, host):
        start = time.time()
        subdomains = self.scan_remote_host_dnsmap(host)
        self.scan_remote_host_nmap(subdomains)
        output('Completion time: {} second(s)'.format(round(time.time() - start, 2)))

    def scan_remote_host_dnsmap(self, host):
        if not self.check_host(host):
            return 'Wrong host: "{}"'.format(host)
        output('Scanning for subdomains...')
        os.system('dnsmap {} >> temp/dnsmap.txt'.format(host))
        with open('temp/dnsmap.txt') as f:
            dnsmap_scan = f.read()
        os.remove('temp/dnsmap.txt')
        output(dnsmap_scan)
        subdomains = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", dnsmap_scan)
        if '127.0.0.1' in subdomains:
            del subdomains[subdomains.index('127.0.0.1')]
        return subdomains

    def scan_remote_host_nmap(self, subdomains):
        output('\nScanning subdomains...')
        self.scanner.scan(' '.join(subdomains), '22-443', '-sV -A -T4')
        output(self.dm.save_csv(self.scanner, 'remote_host'))
