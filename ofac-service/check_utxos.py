import json
import requests
import utils
import sanction
import subprocess
from pyln.client import LightningRpc, RpcError

def get_channels(lightningCli):
    try:
        # Use lightningCli to directly fetch the list of peer channels
        data = lightningCli.listpeerchannels()
        
        # Extract the channels list
        channels = data["channels"]
        return channels

    except RpcError as e:
        print("Error fetching channels:", e)
        return None

def get_funding_utxo_address(settings_data, txid, vout):
    
    url = "%s/api/tx/%s" % (settings_data["esploraUrl"], txid)

    response = requests.get(url)

    data = json.loads(response.text)

    address = data['vin'][vout]['prevout']['scriptpubkey_address']

    return address

def close_channel(lightningCli, channel_id):
    try:
        # Use lightningCli to directly close the specified channel
        response = lightningCli.close(channel_id)
        # Print the response from the close command
        print("response - close_channel")
        print(response)
    except RpcError as e:
        print("Error closing channel:", e)

def execute(lightningCli):
     
    settings_data = utils.get_settings_data()

    channels = get_channels(lightningCli)

    relevant_channels = [channel for channel in channels if channel['state'] == 'CHANNELD_NORMAL' and channel['opener'] == 'remote']

    print("Channels:")
    for channel in relevant_channels:
        short_channel_id = channel['short_channel_id']

        txid = channel['funding_txid']
        vout = channel['funding_outnum']

        address = get_funding_utxo_address(settings_data, txid, vout)

        if sanction.is_sanctioned_address(address):
            close_channel(lightningCli, short_channel_id)

if __name__ == '__main__':
    execute()
