import json
import requests
import utils
import subprocess
from pyln.client import LightningRpc, RpcError

def get_peer_addresses(lightningCli):
    try:
        data = lightningCli.listpeers()
        return data
    except RpcError as e:
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

def get_peer_channels(lightningCli, peer_id):
    try:
        # Use lightningCli to directly fetch the list of channels for the specific peer
        data = lightningCli.listpeerchannels(peer_id)
        channels = data["channels"]
        # Filter channels that are in the 'CHANNELD_NORMAL' state
        return [channel for channel in channels if channel['state'] == 'CHANNELD_NORMAL']
    except RpcError as e:
        print("Error fetching peer channels:", e)
        return None
    
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
    ip_list_file = 'sanctioned_ips.txt'

    with open(ip_list_file, 'r') as file:
        ip_patterns = [line.strip() for line in file if line.strip()]

    peer_addresses = get_peer_addresses(lightningCli)

    for peer in peer_addresses['peers']:
        peer_id = peer['id']
        for netaddr in peer['netaddr']:
            if ip_in_list(netaddr, ip_patterns):
                channels = get_peer_channels(lightningCli, peer_id)
                for channel in channels:
                    short_channel_id = channel['short_channel_id']
                    close_channel(lightningCli, short_channel_id)
                break

if __name__ == '__main__':
    execute()
