import json
import requests
import utils
import sanction

def get_channels(settings_data):
    rpc_method = "v1/listpeerchannels"

    url = "%s/%s" % (settings_data["nodeRestUrl"], rpc_method)
    global rune
    headers = {
        "content-type": "application/json",
        "Rune": rune
    }

    response = requests.post(url, headers=headers)

    data = json.loads(response.text)

    channels = data["channels"]

    return channels

def get_funding_utxo_address(settings_data, txid, vout):
    
    url = "%s/api/tx/%s" % (settings_data["esploraUrl"], txid)

    response = requests.get(url)

    data = json.loads(response.text)

    address = data['vin'][vout]['prevout']['scriptpubkey_address']

    return address

def close_channel(settings_data, channel_id):

    rpc_method = "v1/close"

    url = "%s/%s" % (settings_data["nodeRestUrl"], rpc_method)

    payload = { "id": channel_id }
    global rune
    headers = {
        "content-type": "application/json",
        "Rune": rune
    }

    response = requests.post(url, headers=headers, json=payload)

    print("response - close_channel")
    print(response.text)

def execute():
     
    settings_data = utils.get_settings_data()

    channels = get_channels(settings_data)

    relevant_channels = [channel for channel in channels if channel['state'] == 'CHANNELD_NORMAL' and channel['opener'] == 'remote']

    print("Channels:")
    for channel in relevant_channels:
        short_channel_id = channel['short_channel_id']

        txid = channel['funding_txid']
        vout = channel['funding_outnum']

        address = get_funding_utxo_address(settings_data, txid, vout)

        if sanction.is_sanctioned_address(address):
            close_channel(settings_data, short_channel_id)

if __name__ == '__main__':
    execute()
