import csv
import os


class DataManager:
    file_path = 'scan_{}.csv'

    def save_csv(self, scanner, host, file_name):
        if not os.path.exists(self.file_path.format(file_name)) \
                or not os.stat(self.file_path.format(file_name)).st_size:
            self.csv_write_header(self.file_path.format(file_name))
        self.csv_write_row(scanner, host, self.file_path.format(file_name))

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
    def csv_write_row(scanner, host, file_path):
        with open(file_path, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            if host in scanner.__dict__['_scan_result']['scan']:
                if 'osmatch' in scanner[host] and scanner[host]['osmatch']:
                    os_name = scanner[host]['osmatch'][0]['name']
                else:
                    os_name = ''
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
                                os_name
                            ]
                            writer.writerow(csv_row)

    def save_csv_device(self, scanner, file_name):
        with open(self.file_path.format(file_name), 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            headers = ['host', 'hostname', 'os', 'type']
            writer.writerow(headers)
            for host in scanner.all_hosts():
                csv_row = [host, scanner[host]['hostnames'][0]['name']]
                if 'osmatch' in scanner[host] and scanner[host]['osmatch']:
                    csv_row.append(scanner[host]['osmatch'][0]['name'])
                    csv_row.append(scanner[host]['osmatch'][0]['osclass'][0]['type'])
                else:
                    csv_row.extend(['Unknown', 'Unknown'])
                writer.writerow(csv_row)
        return 'Scan results saved to: "{}"'.format(self.file_path.format(file_name))
