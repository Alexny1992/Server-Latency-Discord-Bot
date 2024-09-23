import psycopg2
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv


def insert_data(channel: str, avg_ping: float, std: float) -> None:
    hostname = os.getenv('DB_HOST')
    database = os.getenv('DB_NAME')
    usename = os.getenv('DB_USER')
    pwd = os.getenv('DB_PASS')
    port_id = os.getenv('DB_PORT')
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host = hostname,
            dbname = database,
            user = usename,
            password = pwd,
            port = port_id
        )
        cur = conn.cursor()
        
        # creating ping latency table and assign data type to it
        # drop = '''DROP TABLE ping_latency'''
        # create_script =  '''CREATE TABLE ping_latency (
        #     channel VARCHAR(255),
        #     average_latency FLOAT,
        #     standard_deviation FLOAT,
        #     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        #     PRIMARY KEY (channel, timestamp)
        # )'''

        # injecting data created from server ping 
        insert_script = '''
                INSERT INTO ping_latency (channel, average_latency, standard_deviation)
                VALUES (%s, %s, %s)
            '''
        for i in range(len(channel)):
            cur.execute(insert_script, (channel[i], avg_ping[i], std[i]))
        conn.commit()
        
        #Convert channel data type to int for user's input
        alter_table_sql = """
            ALTER TABLE ping_latency
            ALTER COLUMN channel TYPE INTEGER USING channel::integer;
            """
        cur.execute(alter_table_sql)
        
        #Delete data longer than 5 mins
        delete_old_data_sql = """
            DELETE FROM ping_latency
            WHERE timestamp < NOW() - INTERVAL '5 minute'
        """
        cur.execute(delete_old_data_sql)
        conn.commit()
        
        
    except Exception as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
            
def aggregate_data() -> list[str, float, float]:
    hostname = os.getenv('DB_HOST')
    database = os.getenv('DB_NAME')
    usename = os.getenv('DB_USER')
    pwd = os.getenv('DB_PASS')
    port_id = os.getenv('DB_PORT')
    conn = None
    cur = None
    
    try:
        conn = psycopg2.connect(
            host = hostname,
            dbname = database,
            user = usename,
            password = pwd,
            port = port_id
        )
        cur = conn.cursor()
        #Allow user to select specific channel for average latency and standard deviation
        channel_value = [x for x in range(1,41)]
        cal_avg = """
            SELECT AVG(average_latency) AS avg_latency, AVG(standard_deviation) AS standard_deviation
            FROM ping_latency
            WHERE channel = %s 
            AND timestamp >= NOW()::timestamp - INTERVAL '5 minute'
        """
        
        channel_avg_results = []
        for i in channel_value:
            cur.execute(cal_avg, (i,))
            result = cur.fetchone()
            if result: 
                avg_latency, std = result
                channel_avg_results.append((i, avg_latency, std))
        return channel_avg_results


    except Exception as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

def retrive_channel_data(channel):
    hostname = os.getenv('DB_HOST')
    database = os.getenv('DB_NAME')
    usename = os.getenv('DB_USER')
    pwd = os.getenv('DB_PASS')
    port_id = os.getenv('DB_PORT')
    conn = None
    cur = None
    
    try:
        conn = psycopg2.connect(
            host = hostname,
            dbname = database,
            user = usename,
            password = pwd,
            port = port_id
        )
        cur = conn.cursor()
        
        retrieve_data = """
            SELECT average_latency, standard_deviation
            FROM ping_latency
            WHERE channel = %s 
            AND timestamp >= NOW() - INTERVAL '5 minute'
        """
        
        # Fetch one result
        cur.execute(retrieve_data, (channel,))
        data = cur.fetchall()
        return data 
    
    except Exception as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
            
