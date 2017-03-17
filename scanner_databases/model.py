import json
import os

import yaml
import psycopg2
import mysql.connector
import pymssql

from .view import show_sql
from .data_manager import DataManager


class ScannerDatabase:
    def __init__(self):
        self.dm = DataManager()

        if os.path.exists('scanner_databases/credentials.json'):
            with open('scanner_databases/credentials.json', 'r') as file:
                self.credentials = json.loads(file.read())

        with open('scanner_databases/sql_data.yml', 'r') as config:
            self.sql_data = yaml.load(config)

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
        show_sql(query, conn, 'employees')
        cursor.execute(query)
        search = cursor.fetchall()
        return self.dm.save_csv(search, 'mysql')

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
        show_sql(query, conn, 'employees')
        cursor.execute(query)
        search = cursor.fetchall()
        return self.dm.save_csv(search, 'mssql')

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
        show_sql(query, conn, 'employees')
        cursor.execute(query)
        search = cursor.fetchall()
        return self.dm.save_csv(search, 'postgresql')
