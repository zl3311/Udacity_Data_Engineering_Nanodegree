import configparser
import psycopg2
import json
import pandas as pd


def count_records(cur, conn, df):
    """Check consistency of record count.
    :params cur: cursor
    :params conn: DB connection
    :params df: metadata dataframe
    """

    for row in df.iterrows():
        table = row[1]['table']
        expected_rows = row[1]['expected_rows']
        
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            records = cur.fetchone()[0]
        except psycopg2.Error as e:
            print(e)

        if records == expected_rows:
            print(f"Number of records matched. Found {records} rows, Expected {expected_rows} rows")
        else:
            print(f"Number of records don't match. Found {records} rows, Expected {expected_rows} rows") 


def check_exist(cur, conn, df):
    """Check if the table exists.
    :params cur: cursor
    :params conn: DB connection
    :params df: metadata dataframe
    """
   
    for row in df.iterrows():
        table = row[1]['table']

        try:
            cur.execute(f"SELECT * FROM {table} LIMIT 5")
            records = cur.fetchone()[0]
            print(f"Table {table} exists")
        except psycopg2.Error as e:
            print(f"Can't find Table {table}")
            print(e)
        

def main():
    config = configparser.ConfigParser()
    config.read('./aws/credentials.cfg')
    
    with open('./metadata.json') as f:
        data = json.load(f)

    df_metadata = pd.DataFrame.from_dict(data)

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    count_records(cur, conn, df_metadata)
    check_null(cur, conn, df_metadata)
    
    conn.close()


if __name__ == "__main__":
    main()