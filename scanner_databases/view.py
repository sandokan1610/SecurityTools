import pandas.io.sql as pdsql


def show_sql(query, conn, name):
    print("######################## {} ########################".format(name.upper()))
    print(pdsql.read_sql_query(query, conn))
