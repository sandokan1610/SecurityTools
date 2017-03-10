import csv
import os


class DataManager:
    file_name = 'scan_nmap.{}'

    def save_csv(self, scanner, subdomain):
        file_path = self.file_name.format('csv')
        if os.path.exists(file_path) and os.stat(file_path).st_size:
            self.csv_write_row(scanner, subdomain, file_path)
        else:
            self.csv_write_header(file_path)

    @staticmethod
    def csv_write_header(file_path):
        with open(file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            csv_header = [
                'host',
                'hostname',
                'hostname_type',
                'protocol',
                'port',
                'name',
                'state',
                'product',
                'extrainfo',
                'reason',
                'version',
                'conf',
                'cpe',
                'os'
            ]
            writer.writerow(csv_header)

    @staticmethod
    def csv_write_row(scanner, subdomain, file_path):
        with open(file_path, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            if subdomain in scanner.__dict__['_scan_result']['scan']:
                if 'osmatch' in scanner[subdomain] and scanner[subdomain]['osmatch']:
                    os_name = scanner[subdomain]['osmatch'][0]['name']
                else:
                    os_name = ''
                for proto in scanner[subdomain].all_protocols():
                    if proto not in ['tcp', 'udp']:
                        continue
                    lport = list(scanner[subdomain][proto].keys())
                    lport.sort()
                    for port in lport:
                        for h in scanner[subdomain]['hostnames']:
                            hostname = h['name']
                            hostname_type = h['type']
                            csv_row = [
                                subdomain, hostname, hostname_type,
                                proto, port,
                                scanner[subdomain][proto][port]['name'],
                                scanner[subdomain][proto][port]['state'],
                                scanner[subdomain][proto][port]['product'],
                                scanner[subdomain][proto][port]['extrainfo'],
                                scanner[subdomain][proto][port]['reason'],
                                scanner[subdomain][proto][port]['version'],
                                scanner[subdomain][proto][port]['conf'],
                                scanner[subdomain][proto][port]['cpe'],
                                os_name
                            ]
                            writer.writerow(csv_row)
