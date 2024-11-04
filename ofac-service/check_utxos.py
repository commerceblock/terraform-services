import json
import requests
import utils
import sanction
from lightning import run_lightning_cli

def get_channels():
    try:
        # Use run_lightning_cli to fetch the list of peer channels
        data = run_lightning_cli("listpeerchannels")
        
        # Parse the JSON response
        data_json = json.loads(data)
        channels = data_json.get("channels", [])
        return channels

    except Exception as e:
        print("Error fetching channels:", e)
        return None

def get_funding_utxo_address(settings_data, txid, vout):
    url = f"{settings_data['esploraUrl']}/api/tx/{txid}"
    response = requests.get(url)
    data = response.json()
    address = data['vin'][vout]['prevout']['scriptpubkey_address']
    return address

def close_channel(channel_id):
    try:
        # Use run_lightning_cli to close the specified channel
        response = run_lightning_cli(f"close {channel_id}")
        print("Response from close_channel:", response)
    except Exception as e:
        print("Error closing channel:", e)

def execute():
    settings_data = utils.get_settings_data()
    channels = get_channels()

    if channels is None:
        print("No channels found.")
        return

    # Filter for relevant channels
    relevant_channels = [channel for channel in channels if channel['state'] == 'CHANNELD_NORMAL' and channel['opener'] == 'remote']
    
    print("Channels:")
    for channel in relevant_channels:
        short_channel_id = channel['short_channel_id']
        txid = channel['funding_txid']
        vout = channel['funding_outnum']

        address = get_funding_utxo_address(settings_data, txid, vout)

        if sanction.is_sanctioned_address(address):
            close_channel(short_channel_id)

if __name__ == '__main__':
    execute()
