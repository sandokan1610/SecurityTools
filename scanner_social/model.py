import json
import os
import time
import logging

import facebook
import vk_requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from view import output
from .view import output_vk, output_fb, output_ld


class ScannerSocial:
    def __init__(self):
        if os.path.exists('scanner_social/credentials.json'):
            with open('scanner_social/credentials.json', 'r') as file:
                self.credentials = json.loads(file.read())

    def scan(self, query):
        if not hasattr(self, 'credentials'):
            return output('Credentials for social networks was not found, did you create credentials.json?')
        self.scan_vk(query)
        self.scan_fb(query)
        self.scan_ld(query)

    def scan_vk(self, query):
        if not self.credentials['vk_app_id'] or not self.credentials['vk_login'] or not self.credentials['vk_pass']:
            return output('VK credentials not founded')
        logging.getLogger('vk-requests').setLevel(logging.ERROR)
        api = vk_requests.create_api(app_id=self.credentials['vk_app_id'],
                                     login=self.credentials['vk_login'],
                                     password=self.credentials['vk_pass'])
        return output_vk(api.users.search(q=query, fields='domain'))

    def fb_token_check(self, token):
        graph = facebook.GraphAPI()
        token_info = graph.debug_access_token(token, self.credentials['fb_app_id'], self.credentials['fb_app_secret'])
        return token_info['data']['is_valid']

    def fb_get_token(self):
        if self.credentials['fb_extended_user_token'] \
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
            return output('Facebook credentials not founded')

        access_token = self.fb_get_token()
        if not access_token:
            return output('Facebook tokens expired, get new at: https://developers.facebook.com/tools/accesstoken/')

        graph = facebook.GraphAPI(access_token)
        args = {'q': query, 'type': 'user', 'fields': 'name,link'}
        request = graph.request('/search?{}'.format(query), args=args)
        return output_fb(request)

    def scan_ld(self, query):
        if not self.credentials['ld_login'] or not self.credentials['ld_pass']:
            return output('Linkedin credentials not founded')
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
                return output_ld(search)
