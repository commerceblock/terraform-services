from collections import defaultdict
from datetime import datetime, timedelta
import json
import requests

import utils

def execute(hours=24):
    print("Executing total-fee-income.py")

    settings_data = utils.get_settings_data()

    rpc_method = "v1/bkpr-listaccountevents"

    url = "%s/%s" % (settings_data["nodeRestUrl"], rpc_method)

    global rune
    headers = {
        "content-type": "application/json",
        "Rune": rune
    }

    response = requests.post(url, headers=headers)

    data = json.loads(response.text)

    start_time = int((datetime.now() - timedelta(hours=hours)).timestamp())

    # Filter the events to remove those older than 24 hours
    filtered_events = [event for event in data['events'] if event['timestamp'] >= start_time]

    # Update the data dictionary with the filtered events
    data['events'] = filtered_events

    return data
