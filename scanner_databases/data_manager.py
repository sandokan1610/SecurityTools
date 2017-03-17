import csv
import yaml


class DataManager:
    def __init__(self):
        with open('config.yml', 'r') as config:
            self.config = yaml.load(config)

    def save_csv(self, search, file_name):
        file_path = '{}scanner_{}.csv'.format(self.config['path_output'], file_name)
        with open(file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            headers = ['city_id', 'first_name', 'last_name', 'phone_number', 'employee_id', 'city', 'population']
            writer.writerow(headers)
            for row in search:
                writer.writerow(row)
        return 'Scan results saved to: "{}"'.format(file_path.format(file_name))
