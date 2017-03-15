import socket
import os
import re
import time
import logging
import json
import yaml

import nmap
import psycopg2 as psycopg2
import vk_requests
import facebook
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import mysql.connector
import pymssql

from view import View
from data_manager import DataManager


class Model:
    def __init__(self):
        self.view = View()
        self.dm = DataManager()
        self.scanner = nmap.PortScanner()
        if os.path.exists('credentials.json'):
            with open('credentials.json', 'r') as file:
                self.credentials = json.loads(file.read())

        with open('sql_data.yml', 'r') as config:
            self.sql_data = yaml.load(config)

    @staticmethod
    def check_host(host):
        try:
            socket.gethostbyname(host)
            return True
        except socket.gaierror:
            return False

    def scan_remote_host(self, host):
        start = time.time()
        subdomains = self.scan_remote_host_dnsmap(host)
        self.scan_remote_host_nmap(subdomains)
        return 'Completion time: {} second(s)'.format(round(time.time() - start, 2))

    def scan_remote_host_dnsmap(self, host):
        if not self.check_host(host):
            return 'Wrong host: "{}"'.format(host)
        self.view.output('Scanning for subdomains...')
        os.system('dnsmap {} -r dnsmap.txt'.format(host))
        with open('dnsmap.txt') as f:
            dnsmap_scan = f.read()
        os.remove('dnsmap.txt')
        subdomains = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", dnsmap_scan)
        if '127.0.0.1' in subdomains:
            del subdomains[subdomains.index('127.0.0.1')]
        return subdomains

    def scan_remote_host_nmap(self, subdomains):
        self.view.output('\nScanning subdomains...')
        self.scanner.scan(hosts=' '.join(subdomains),
                                ports='22-443',
                                arguments='-sV -A -T4')
        self.dm.save_csv_remote_host(self.scanner, 'remote_host')
        self.view.output('Scan results saved to: "{}"'.format(self.dm.file_path.format('remote_host')))

    def scan_network(self, network):
        self.view.output('Scanning network...')
        start = time.time()
        self.scanner.scan(network or '192.168.1.0/24', arguments='-O -T5')
        self.view.output('Completion time: {} second(s)'.format(round(time.time() - start, 2)))
        return self.dm.save_csv_network(self.scanner, 'network')

    def scan_social(self, query):
        if not hasattr(self, 'credentials'):
            return self.view.output('Credentials for social networks was not found'
                                    ', did you create credentials.json?')
        self.scan_vk(query)
        self.scan_fb(query)
        self.scan_ld(query)

    def scan_vk(self, query):
        if not self.credentials['vk_app_id'] or not self.credentials['vk_login'] or not self.credentials['vk_pass']:
            return self.view.output('VK credentials not founded')
        logging.getLogger('vk-requests').setLevel(logging.ERROR)
        api = vk_requests.create_api(app_id=self.credentials['vk_app_id'],
                                     login=self.credentials['vk_login'],
                                     password=self.credentials['vk_pass'])
        return self.view.output_vk(api.users.search(q=query, fields='domain'))

    def fb_token_check(self, token):
        graph = facebook.GraphAPI()
        token_info = graph.debug_access_token(token, self.credentials['fb_app_id'], self.credentials['fb_app_secret'])
        return token_info['data']['is_valid']

    def fb_get_token(self):
        if 'fb_extended_user_token' in self.credentials \
                and self.credentials['fb_extended_user_token'] \
                and self.fb_token_check(self.credentials['fb_extended_user_token']):
            return self.credentials['fb_extended_user_token']
        elif self.fb_token_check(self.credentials['fb_user_token']):
            graph = facebook.GraphAPI(self.credentials['fb_user_token'])
            extend_token = graph.extend_access_token(self.credentials['fb_app_id'],
                                                     self.credentials['fb_app_secret'])
            self.credentials["fb_extended_user_token"] = extend_token['access_token']
            with open('credentials.json', 'w') as outfile:
                json.dump(self.credentials, outfile, indent=4)
            return extend_token['access_token']

    def scan_fb(self, query):
        if not self.credentials['fb_user_token'] \
                or not self.credentials['fb_app_id'] \
                or not self.credentials['fb_app_secret']:
            return self.view.output('Facebook credentials not founded')

        access_token = self.fb_get_token()
        if not access_token:
            return self.view.output('Facebook tokens expired, get new at: '
                                    'https://developers.facebook.com/tools/accesstoken/')

        graph = facebook.GraphAPI(access_token)
        args = {'q': query, 'type': 'user', 'fields': 'name,link'}
        request = graph.request('/search?{}'.format(query), args=args)
        return self.view.output_fb(request)

    def scan_ld(self, query):
        if not self.credentials['ld_login'] or not self.credentials['ld_pass']:
            return self.view.output('Linkedin credentials not founded')
        browser = webdriver.Firefox()

        browser.get('https://www.linkedin.com/')

        elem = browser.find_element_by_class_name('login-email')
        elem.send_keys(self.credentials['ld_login'])

        elem = browser.find_element_by_class_name('login-password')
        elem.send_keys(self.credentials['ld_pass'] + Keys.RETURN)

        time.sleep(5.0)
        browser.get(
            'https://www.linkedin.com/search/results/index/?keywords={}&origin=GLOBAL_SEARCH_HEADER'.format(query))

        content = browser.page_source.splitlines()

        browser.quit()

        for line in content:
            if 'metadata' in line:
                metadata = json.loads(line)
                search = [person for person in metadata['included']
                          if 'publicIdentifier' in person and person['$deletedFields']]
                return self.view.output_ld(search)

    @staticmethod
    def check_fields(first_name, last_name, phone_number):
        if not (first_name and last_name and phone_number):
            return 'All fields must be filled.'
        if not first_name.isalpha() or not last_name.isalpha():
            return 'Name must be a string.'
        if not phone_number.isdigit():
            return 'Phone number must be an integer.'

    def connect_mysql(self):
        conn = mysql.connector.connect(user=self.credentials['mysql_user'],
                                       password=self.credentials['mysql_password'],
                                       host=self.credentials['mysql_host'],
                                       database=self.credentials['mysql_database'])
        cursor = conn.cursor()
        return conn, cursor

    def prepare_mysql(self, cursor):
        cursor.execute("DROP TABLE IF EXISTS city_test_1, employees_test_1;")

        cursor.execute("CREATE TABLE city_test_1 (id INTEGER AUTO_INCREMENT PRIMARY KEY, name CHAR(20) , "
                       "population INTEGER);")
        cursor.execute("CREATE TABLE employees_test_1 (city_id INTEGER, first_name CHAR(20), last_name CHAR(20), "
                       "phone_number INTEGER);")

        cursor.executemany("INSERT INTO city_test_1(name, population) VALUES (%(name)s, %(population)s);",
                           self.sql_data['city_data'])
        cursor.executemany("INSERT INTO employees_test_1(city_id, first_name, last_name, phone_number) "
                           "VALUES (%(city_id)s, %(first_name)s, %(last_name)s, %(phone_number)s)",
                           self.sql_data['employees_data'])

    def scan_mysql(self, conn, cursor, first_name, last_name, phone_number):
        if self.check_fields(first_name, last_name, phone_number):
            return self.check_fields(first_name, last_name, phone_number)
        self.prepare_mysql(cursor)
        query = "SELECT * FROM employees_test_1 " \
                "INNER JOIN city_test_1 ON (employees_test_1.city_id = city_test_1.id) " \
                "WHERE first_name='{}' OR last_name='{}' OR phone_number='{}';".format(first_name, last_name,
                                                                                       phone_number)
        self.view.show_sql(query, conn, 'employees')
        cursor.execute(query)
        search = cursor.fetchall()
        return self.dm.save_sql(search, 'mysql')

    def connect_mssql(self):
        conn = pymssql.connect(host=self.credentials['mssql_host'],
                               user=self.credentials['mssql_user'],
                               password=self.credentials['mssql_password'],
                               database=self.credentials['mssql_database'])
        cursor = conn.cursor()
        return conn, cursor

    def prepare_mssql(self, cursor):
        cursor.execute("DROP TABLE IF EXISTS city_test_1, employees_test_1;")

        cursor.execute("CREATE TABLE city_test_1 (id INT IDENTITY(1,1) PRIMARY KEY, name VARCHAR(7), population INT);")
        cursor.execute("CREATE TABLE employees_test_1 (city_id INT, first_name VARCHAR(5), last_name VARCHAR(9), "
                       "phone_number INT);")

        cursor.executemany("INSERT INTO city_test_1(name, population) VALUES (%(name)s, %(population)s);",
                           self.sql_data['city_data'])
        cursor.executemany("INSERT INTO employees_test_1(city_id, first_name, last_name, phone_number) "
                           "VALUES (%(city_id)s, %(first_name)s, %(last_name)s, %(phone_number)s);",
                           self.sql_data['employees_data'])

    def scan_mssql(self, conn, cursor, first_name, last_name, phone_number):
        if self.check_fields(first_name, last_name, phone_number):
            return self.check_fields(first_name, last_name, phone_number)
        self.prepare_mssql(cursor)
        query = "SELECT * FROM employees_test_1 " \
                "INNER JOIN city_test_1 ON (employees_test_1.city_id = city_test_1.id) " \
                "WHERE first_name='{}' OR last_name='{}' OR phone_number='{}';".format(first_name, last_name,
                                                                                       phone_number)
        self.view.show_sql(query, conn, 'employees')
        cursor.execute(query)
        search = cursor.fetchall()
        return self.dm.save_sql(search, 'mssql')

    def connect_postgresql(self):
        conn = psycopg2.connect(database=self.credentials['postgresql_database'],
                                user=self.credentials['postgresql_user'],
                                password=self.credentials['postgresql_password'],
                                host=self.credentials['postgresql_host'])
        cursor = conn.cursor()
        return conn, cursor

    def prepare_postgresql(self, cursor):
        cursor.execute("DROP TABLE IF EXISTS city_test_1, employees_test_1;")

        cursor.execute("CREATE TABLE city_test_1 (id SERIAL PRIMARY KEY, name CHAR(7), population INTEGER);")
        cursor.execute("CREATE TABLE employees_test_1 (city_id INTEGER, first_name CHAR(5), last_name CHAR(9), "
                       "phone_number INTEGER);")

        cursor.executemany("INSERT INTO city_test_1(name, population) VALUES (%(name)s, %(population)s);",
                           self.sql_data['city_data'])
        cursor.executemany("INSERT INTO employees_test_1(city_id, first_name, last_name, phone_number) "
                           "VALUES (%(city_id)s, %(first_name)s, %(last_name)s, %(phone_number)s)",
                           self.sql_data['employees_data'])

    def scan_postgresql(self, conn, cursor, first_name, last_name, phone_number):
        if self.check_fields(first_name, last_name, phone_number):
            return self.check_fields(first_name, last_name, phone_number)
        self.prepare_postgresql(cursor)
        query = "SELECT * FROM employees_test_1 " \
                "INNER JOIN city_test_1 ON (employees_test_1.city_id = city_test_1.id) " \
                "WHERE first_name='{}' OR last_name='{}' OR phone_number='{}';".format(first_name, last_name,
                                                                                       phone_number)
        self.view.show_sql(query, conn, 'employees')
        cursor.execute(query)
        search = cursor.fetchall()
        return self.dm.save_sql(search, 'postgresql')
