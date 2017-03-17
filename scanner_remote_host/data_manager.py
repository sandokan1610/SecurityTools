import csv
import os
import yaml


class DataManager:
    def __init__(self):
        with open('config.yml', 'r') as config:
            self.config = yaml.load(config)

    def save_csv(self, scanner, file_name):
        file_path = '{}scanner_{}.csv'.format(self.config['path_output'], file_name)
        if not os.path.exists(file_path) \
                or not os.stat(file_path).st_size:
            self.csv_write_header(file_path)
        self.csv_write_row(scanner, file_path)
        return 'Scan results saved to: "{}"'.format(file_path)

    @staticmethod
    def csv_write_header(file_path):
        with open(file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            csv_header = [
                'host', 'hostname', 'hostname_type',
                'protocol', 'port', 'name',
                'state', 'product', 'extra_info',
                'reason', 'version', 'conf',
                'cpe', 'os', 'type'
            ]
            writer.writerow(csv_header)

    @staticmethod
    def csv_write_row(scanner, file_path):
        with open(file_path, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            for host in scanner.all_hosts():
                if 'osmatch' in scanner[host] and scanner[host]['osmatch']:
                    os_name = scanner[host]['osmatch'][0]['name']
                    device_type = scanner[host]['osmatch'][0]['osclass'][0]['type']
                else:
                    os_name = 'Undefined'
                    device_type = 'Undefined'
                for proto in scanner[host].all_protocols():
                    if proto not in ['tcp', 'udp']:
                        continue
                    lport = list(scanner[host][proto].keys())
                    lport.sort()
                    for port in lport:
                        for h in scanner[host]['hostnames']:
                            hostname = h['name']
                            hostname_type = h['type']
                            csv_row = [
                                host, hostname, hostname_type,
                                proto, port,
                                scanner[host][proto][port]['name'],
                                scanner[host][proto][port]['state'],
                                scanner[host][proto][port]['product'],
                                scanner[host][proto][port]['extrainfo'],
                                scanner[host][proto][port]['reason'],
                                scanner[host][proto][port]['version'],
                                scanner[host][proto][port]['conf'],
                                scanner[host][proto][port]['cpe'],
                                os_name, device_type
                            ]
                            writer.writerow(csv_row)
