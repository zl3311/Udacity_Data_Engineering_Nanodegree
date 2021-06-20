import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries
import sys


def load_staging_tables(cur, conn):
    """Load staging tables.
    :params cur: cursor
    :params conn: DB connection
    """
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    """Insert tables.
    :params cur: cursor
    :params conn: DB connection
    """
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    config = configparser.ConfigParser()
    config.read('./aws/credentials.cfg')
    
    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))    
    cur = conn.cursor()
        
    try:
        load_staging_tables(cur, conn)
    except psycopg2.Error as e:
        print(e)
        sys.exit()
        
    try:
        insert_tables(cur, conn)
    except psycopg2.Error as e:
        print(e)
        
    conn.close()
    
if __name__ == "__main__":
    main()