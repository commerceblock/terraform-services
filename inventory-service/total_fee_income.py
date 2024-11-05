# total-fee-income.py
from collections import defaultdict
from datetime import datetime, timedelta
import json
import requests
import utils
from lightning import run_lightning_cli

def execute(hours=24):
    print("Executing total-fee-income.py")

    try:
        # Run lightning-cli command to get account events
        output = run_lightning_cli("bkpr-listaccountevents")
        
        if not output:
            print("No output from lightning-cli.")
            return {}
        
        # Parse JSON output from lightning-cli
        data = json.loads(output)
        
        # Calculate total fee income based on the parsed data
        return calculate_total_fee_income(data, hours)
        
    except Exception as e:
        print("Error executing lightning-cli command:", e)
        return {}
    
def calculate_total_fee_income(data, hours=24):
    """
    Calculate the total fee income grouped by type for the last 'hours' hours.

    Parameters:
    data (dict): Parsed JSON data containing the event data.
    hours (int): The number of hours to look back from the current time. Default is 24.

    Returns:
    dict: A dictionary with the aggregated sums grouped by type.
    """
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
