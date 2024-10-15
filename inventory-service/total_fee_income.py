# total-fee-income.py
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

    headers = {
        "content-type": "application/json",
        "Rune": settings_data["rune"]
    }

    response = requests.post(url, headers=headers)

    return calculate_total_fee_income(response.text, hours)
    
def calculate_total_fee_income(json_data, hours=24):
    """
    Calculate the total fee income grouped by type for the last 'hours' hours.

    Parameters:
    json_data (str): JSON string containing the event data.
    hours (int): The number of hours to look back from the current time. Default is 24.

    Returns:
    dict: A dictionary with the aggregated sums grouped by type.
    """
    # Parse the JSON data
    data = json.loads(json_data)

    # Get the current time
    current_time = datetime.now()

    # Dictionary to hold the aggregated sums for the given time range, grouped by type
    aggregated_values_by_type = defaultdict(lambda: {'credit_msat': 0, 'debit_msat': 0, 'total': 0})

    # Process each event
    for event in data['events']:
        # Convert the timestamp to a datetime object
        event_time = datetime.fromtimestamp(event['timestamp'])
        
        # Check if the event is within the last 'hours' hours
        if current_time - timedelta(hours=hours) <= event_time <= current_time:
            event_type = event['type']
            credit = event.get('credit_msat', 0)
            debit = event.get('debit_msat', 0)
            
            aggregated_values_by_type[event_type]['credit_msat'] += credit
            aggregated_values_by_type[event_type]['debit_msat'] += debit
            aggregated_values_by_type[event_type]['total'] += credit - debit

    # Convert defaultdict to a regular dictionary before returning
    return dict(aggregated_values_by_type)

