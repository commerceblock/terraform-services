import json
import requests
import utils

def get_peer_addresses(settings_data):
    rpc_method = "v1/listpeers"

    url = "%s/%s" % (settings_data["nodeRestUrl"], rpc_method)

    global rune
    headers = {
        "content-type": "application/json",
        "Rune": rune
    }

    response = requests.post(url, headers=headers)

    data = json.loads(response.text)

    return data

def ip_in_list(ip_with_port, ip_patterns):
    # Extract the IP part from the given IP:Port string
    ip_to_check = ip_with_port.split(':')[0]
    
    # Function to check if an IP matches an IP pattern with wildcards
    def ip_matches_pattern(ip, pattern):
        ip_parts = ip.split('.')
        pattern_parts = pattern.split('.')

        for ip_part, pattern_part in zip(ip_parts, pattern_parts):
            if pattern_part != '*' and ip_part != pattern_part:
                return False
        return True

    # Check if the IP matches any pattern in the list
    for pattern in ip_patterns:
        if ip_matches_pattern(ip_to_check, pattern):
            return True

    return False

def get_peer_channels(settings_data, peer_id):
    rpc_method = "v1/listpeerchannels"

    url = "%s/%s" % (settings_data["nodeRestUrl"], rpc_method)

    payload = { "id": peer_id }
    global rune
    headers = {
        "content-type": "application/json",
        "Rune": rune
    }

    response = requests.post(url, headers=headers, json=payload)

    data = json.loads(response.text)

    channels = data["channels"]

    return [channel for channel in channels if channel['state'] == 'CHANNELD_NORMAL']

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

    ip_list_file = 'sanctioned_ips.txt'

    with open(ip_list_file, 'r') as file:
        ip_patterns = [line.strip() for line in file if line.strip()]

    peer_addresses = get_peer_addresses(settings_data)

    for peer in peer_addresses['peers']:
        peer_id = peer['id']
        for netaddr in peer['netaddr']:
            if ip_in_list(netaddr, ip_patterns):
                channels = get_peer_channels(settings_data, peer_id)
                for channel in channels:
                    short_channel_id = channel['short_channel_id']
                    close_channel(settings_data, short_channel_id)
                break

if __name__ == '__main__':
    execute()
