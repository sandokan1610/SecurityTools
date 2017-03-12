class View:
    @staticmethod
    def output(text):
        print(text)

    @staticmethod
    def output_vk(res):
        for x in res['items']:
            print('{} {} - https://vk.com/{}'.format(x['first_name'], x['last_name'], x['domain']))

    @staticmethod
    def output_fb(res):
        for x in res['data']:
            print('{} - {}'.format(x['name'], x['link']))

    @staticmethod
    def output_ld(res):
        for x in res:
            print('{} {} - https://www.linkedin.com/in/{}/'
                  .format(x.get('firstName', ''), x.get('lastName', 'Участник Linkedin'), x['publicIdentifier']))

    @staticmethod
    def inp(text):
        return input(text)
