import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    """Drop tables if they already exist.
    :params cur: cursor
    :params conn: DB connection
    """
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()
        
def create_tables(cur, conn):
    """Create tables.
    :params cur: cursor
    :params conn: DB connection
    """
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()

def main():
    config = configparser.ConfigParser()
    config.read('./aws/credentials.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()

    try:
        drop_tables(cur, conn)
    except psycopg2.Error as e:
        print(e)
        
    try:
        create_tables(cur, conn)
    except psycopg2.Error as e:
        print(e)

    conn.close()


if __name__ == "__main__":
    main()