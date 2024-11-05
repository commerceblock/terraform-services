from collections import defaultdict
from datetime import datetime, timedelta
import json
import requests
import utils
from lightning import run_lightning_cli

def execute(hours=24):
    print("Executing total-fee-income.py with hours:", hours)
    # Run lightning-cli command to get account events
    try:
        output = run_lightning_cli("bkpr-listaccountevents")
        # Parse JSON output from lightning-cli
        data = json.loads(output)
        # Calculate start time based on the hours parameter
        start_time = int((datetime.now() - timedelta(hours=hours)).timestamp())
        # Filter the events to only include those within the last 'hours' hours
        filtered_events = [event for event in data['events'] if event['timestamp'] >= start_time]
        # Update the data dictionary with the filtered events
        data['events'] = filtered_events
        return data

    except Exception as e:
        print("Error executing bkpr-listaccountevents command:", e)
        return None
