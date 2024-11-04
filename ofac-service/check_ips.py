import json
import requests
import utils
from main import run_lightning_cli  # Import the Docker-based command executor

def get_peer_addresses():
    try:
        # Use run_lightning_cli to get the list of peers
        data = run_lightning_cli("listpeers")
        data_json = json.loads(data)
        return data_json
    except Exception as e:
        print("Error fetching peer addresses:", e)
        return None
    
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

def get_peer_channels(peer_id):
    try:
        # Use run_lightning_cli to get channels for a specific peer
        data = run_lightning_cli(f"listpeerchannels {peer_id}")
        data_json = json.loads(data)
        # Filter channels that are in the 'CHANNELD_NORMAL' state
        return [channel for channel in data_json["channels"] if channel['state'] == 'CHANNELD_NORMAL']
    except Exception as e:
        print("Error fetching peer channels:", e)
        return None
    
def close_channel(channel_id):
    try:
        # Use run_lightning_cli to close the specified channel
        response = run_lightning_cli(f"close {channel_id}")
        print("Response from close_channel:", response)
    except Exception as e:
        print("Error closing channel:", e)

def execute():
    ip_list_file = 'sanctioned_ips.txt'

    with open(ip_list_file, 'r') as file:
        ip_patterns = [line.strip() for line in file if line.strip()]

    peer_addresses = get_peer_addresses()

    if peer_addresses is None:
        print("No peer addresses found.")
        return

    for peer in peer_addresses['peers']:
        peer_id = peer['id']
        for netaddr in peer['netaddr']:
            if ip_in_list(netaddr, ip_patterns):
                channels = get_peer_channels(peer_id)
                if channels is not None:
                    for channel in channels:
                        short_channel_id = channel['short_channel_id']
                        close_channel(short_channel_id)
                break

if __name__ == '__main__':
    execute()
