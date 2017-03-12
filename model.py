import socket
import os
import re
import time
import logging
import json

import nmap
import vk_requests
import facebook
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

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

    @staticmethod
    def check_host(host):
        try:
            socket.gethostbyname(host)
            return True
        except socket.gaierror:
            return False

    def scan_dnsmap(self, host):
        if not self.check_host(host):
            return 'Wrong host: "{}"'.format(host)
        self.view.output('Scanning for subdomains...')
        start = time.time()
        os.system('dnsmap {} >> dnsmap.txt'.format(host))
        with open('dnsmap.txt') as f:
            dnsmap_scan = f.read()
        os.remove('dnsmap.txt')
        self.view.output(dnsmap_scan)
        subdomains = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", dnsmap_scan)
        if '127.0.0.1' in subdomains:
            del subdomains[subdomains.index('127.0.0.1')]
        self.scan_nmap(subdomains, start)

    def scan_nmap(self, subdomains, start):
        self.view.output('Scanning founded subdomains...')
        for inx, subdomain in enumerate(subdomains, 1):
            self.scanner.scan(subdomain, '22-443', "-sV -O -A")
            self.dm.save_csv(self.scanner, subdomain)
            self.view.output('{}% completed...'.format(round(inx / len(subdomains) * 100)))
        return 'completion time: {} second(s)'.format(round(time.time() - start, 2))

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
        browser.set_page_load_timeout(30)

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
