import csv


class DataManager:
    file_name = 'scan_nmap.{}'

    def save_txt(self, scan_res):
        with open(self.file_name.format('txt'), 'w') as file:
            file.write(scan_res)
        return 'Successfully saved to .txt file.'

    def save_csv(self, scan_res):
        csv_data = [row.split(';') for row in scan_res.split('\r\n')]
        with open(self.file_name.format('csv'), 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(csv_data[0])
            writer.writerows(csv_data[1:])
        return 'Successfully saved to "{}".'.format(self.file_name.format('csv'))
