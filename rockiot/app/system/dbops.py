#!/usr/bin/env python

import os
from datetime import date

import psycopg2

TS_HOST = os.getenv("TS_HOST", default='localhost')
TS_PORT = int(os.getenv("TS_PORT", default='5432'))
TS_DB = os.getenv("TS_DB", default='rock_iot')
TS_USER = os.getenv("TS_USER", default='postgres')
TS_PASS = os.getenv("TS_PASS", default='postgres')


def export_raw_data_to_csv():

    print("Preparing for data export")

    db_conn = psycopg2.connect(host=TS_HOST, port=TS_PORT, dbname=TS_DB, user=TS_USER, password=TS_PASS)
    db_cursor = db_conn.cursor()

    # Use the COPY function on the SQL we created above.
    query = "SELECT * FROM sensor_data"
    full_query_csv = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(query)

    t_path_n_file = f"/rockiot-data/sensor_data-{date.today().isoformat()}.csv"
    try:
        with open(t_path_n_file, 'w') as f_output:
            db_cursor.copy_expert(full_query_csv, f_output)
        print("Success. Sensor data exported to: " + t_path_n_file)
    except psycopg2.Error as e:
        print("Error: " + e + "/n query we ran: " + query + "/n t_path_n_file: " + t_path_n_file)

    db_cursor.close()
    db_conn.close()
    return t_path_n_file


if __name__ == '__main__':
    export_raw_data_to_csv()
