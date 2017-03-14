import pandas.io.sql as pdsql

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
                  .format(x.get('firstName', ''), x.get('lastName', 'Linkedin User'), x['publicIdentifier']))

    @staticmethod
    def show_sql(query, conn, name):
        print("######################## {} ########################".format(name.upper()))
        print(pdsql.read_sql_query(query, conn))

    @staticmethod
    def inp(text):
        return input(text)
