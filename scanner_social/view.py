def output_vk(res):
    for x in res['items']:
        print('{} {} - https://vk.com/{}'.format(x['first_name'], x['last_name'], x['domain']))


def output_fb(res):
    for x in res['data']:
        print('{} - {}'.format(x['name'], x['link']))


def output_ld(res):
    for x in res:
        print('{} {} - https://www.linkedin.com/in/{}/'
              .format(x.get('firstName', ''), x.get('lastName', 'Linkedin User'), x['publicIdentifier']))
