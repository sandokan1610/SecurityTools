import csv
import yaml


class DataManager:
    def __init__(self):
        with open('config.yml', 'r') as config:
            self.config = yaml.load(config)

    def save_csv(self, scanner, file_name):
        file_path = '{}scanner_{}.csv'.format(self.config['path_output'], file_name)
        with open(file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            headers = ['host', 'hostname', 'os', 'type']
            writer.writerow(headers)
            for host in scanner.all_hosts():
                csv_row = [host, scanner[host]['hostnames'][0]['name']]
                if 'osmatch' in scanner[host] and scanner[host]['osmatch']:
                    csv_row.append(scanner[host]['osmatch'][0]['name'])
                    csv_row.append(scanner[host]['osmatch'][0]['osclass'][0]['type'])
                else:
                    csv_row.extend(['Undefined', 'Undefined'])
                writer.writerow(csv_row)
        return 'Scan results saved to: "{}"'.format(file_path)
