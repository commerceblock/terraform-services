from collections import defaultdict
from datetime import datetime, timedelta
import json
import requests
import psycopg2
import utils
from lightning import run_lightning_cli

def save(settings_data, data_json, start_time, end_time):

    pg_host, pg_port, pg_db, pg_user, pg_password = \
        settings_data["pg_host"], \
        settings_data["pg_port"], \
        settings_data["pg_db"], \
        settings_data["pg_user"], \
        settings_data["pg_password"]

    conn_string = "host=%s port=%s dbname=%s user=%s password=%s" % (pg_host, pg_port, pg_db, pg_user, pg_password)

    conn = psycopg2.connect(conn_string)

    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS cln_stats (id serial PRIMARY KEY, channel varchar, start_time TIMESTAMPTZ, end_time TIMESTAMPTZ, stats_data JSONB);")

    start_time = datetime.fromtimestamp(start_time)
    end_time = datetime.fromtimestamp(end_time)

    # Insert data for each channel
    for channel_data in data_json['channels_apy']:
        account = channel_data['account']  # Extract the account value
        stats_data = json.dumps(channel_data)  # Convert the channel data back to JSON

         # Insert the data into the table
        cur.execute("""
            INSERT INTO cln_stats (channel, start_time, end_time, stats_data)
            VALUES (%s, %s, %s, %s);
            """, (account, start_time, end_time, stats_data))

    conn.commit()

    cur.close()
    conn.close()

def execute(hours):
    print("Executing execute function with hours:", hours)
    # Retrieve settings data
    settings_data = utils.get_settings_data()
    # Calculate start and end times
    start_time = int((datetime.now() - timedelta(hours=hours)).timestamp())
    end_time = int(datetime.now().timestamp())

    try:
        # Run lightning-cli command to get channels APY data
        output = run_lightning_cli(f"bkpr-channelsapy {start_time} {end_time}")
        # Parse JSON output from lightning-cli
        data_json = json.loads(output)
        # Save the data (implement save function as needed)
        save(settings_data, data_json, start_time, end_time)
        return data_json

    except Exception as e:
        print("Error executing bkpr-channelsapy command:", e)
        return None

if __name__ == "__main__":
    execute()
