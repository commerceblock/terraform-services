import configparser
import requests
import subprocess
import time
import json
import logging

def run_command(command):
    """Run a shell command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Command failed: {command}\nError: {result.stderr}")
        return None
    logging.info(f"Command succeeded: {command}\nOutput: {result.stdout.strip()}")
    return result.stdout.strip()

def connect_to_node(node_id, ip_address, port, network, container_name):
    """Connect to a specified node."""
    command = f"sudo docker container exec {container_name} lightning-cli --{network} connect {node_id} {ip_address}:{port}"
    return run_command(command)

def allocate_onchain_address(network, container_name):
    """Allocate an on-chain address to fund the node."""
    command = f"sudo docker container exec {container_name} lightning-cli --{network} newaddr"
    return run_command(command)

def list_funds(network, container_name):
    """List on-chain and channel funds."""
    command = f"sudo docker container exec {container_name} lightning-cli --{network} listfunds"
    return run_command(command)

def list_channels(network, container_name):
    """List all channels."""
    command = f"sudo docker container exec {container_name} lightning-cli --{network} listchannels"
    return run_command(command)

def get_summary(network, container_name):
    """Show node summary status."""
    command = f"sudo docker container exec {container_name} lightning-cli --{network} summary"
    return run_command(command)

def fund_channel(node_id, amount, network, container_name):
    """Fund a channel with a specified amount."""
    command = f"sudo docker container exec {container_name} lightning-cli --{network} fundchannel {node_id} {amount}"
    return run_command(command)

def close_channel(channel_id, network, container_name):
    """Close a specified channel."""
    command = f"sudo docker container exec {container_name} lightning-cli --{network} close {channel_id}"
    return run_command(command)

def electrum_rpc(method, params=None):
    """Send an RPC request to the Electrum server."""
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": method,
        "params": params or []
    }
    response = requests.post(config.get('electrum', 'rpc_url'), json=payload)
    return response.json()

def send_funds_to_address(address, amount):
    """Send funds to the specified address using Electrum."""
    # Unlock wallet if necessary
    password = config.get('electrum', 'wallet_password')
    if password:
        electrum_rpc('walletpassphrase', [password, 60])

    # Create and send transaction
    txid = electrum_rpc('payto', [address, amount])
    electrum_rpc('broadcast', [txid])
    return txid

def main():
    # Configure logging
    logging.basicConfig(filename='lightning_node_setup.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    logging.info("Starting the Lightning node setup script...")

    # Read configuration file
    global config
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Get node connection details
    node_id = config.get('lightning', 'node_id')
    ip_address = config.get('lightning', 'ip_address')
    port = config.get('lightning', 'port')
    network = config.get('lightning', 'network')
    container_name = config.get('lightning', 'container_name')

    # Get channel details
    number_of_channels = config.getint('channels', 'number_of_channels')
    channel_funds = [float(fund) for fund in config.get('channels', 'channel_funds').split(',')]
    node_ids = config.get('channels', 'node_ids').split(',')

    # Validate the number of channels and funds
    if len(channel_funds) != number_of_channels or len(node_ids) != number_of_channels:
        logging.error(f"Number of channels ({number_of_channels}) does not match the number of channel funds ({len(channel_funds)}) or node IDs provided ({len(node_ids)}).")
        raise ValueError(f"Number of channels ({number_of_channels}) does not match the number of channel funds ({len(channel_funds)}) or node IDs provided ({len(node_ids)}).")

    print("Connecting to the node...")
    connect_to_node(node_id, ip_address, port, network, container_name)
    
    if input("Do you want to allocate an on-chain address to fund the node? (yes/no) ").strip().lower() != 'yes':
        print("Operation cancelled.")
        logging.info("Operation cancelled by user.")
        return

    print(f"Allocating an on-chain address to fund the node on {network}...")
    address = allocate_onchain_address(network, container_name)
    if not address:
        logging.error("Failed to allocate on-chain address.")
        return
    print(f"On-chain address allocated: {address}")

    amount_to_send = sum(channel_funds)
    print(f"Total amount to send: {amount_to_send} BTC")
    if input("Do you want to send funds to the allocated address from Electrum? (yes/no) ").strip().lower() != 'yes':
        print("Operation cancelled.")
        logging.info("Operation cancelled by user.")
        return

    print(f"Sending funds to the allocated address from Electrum...")
    txid = send_funds_to_address(address, amount_to_send)
    if not txid:
        logging.error("Failed to send funds from Electrum.")
        return
    print(f"Transaction sent with ID: {txid}")

    # Wait for the transaction to be confirmed
    input("Wait for the transaction to be confirmed and press Enter to continue...")

    print(f"Listing current funds on {network}...")
    funds = list_funds(network, container_name)
    if funds:
        print(funds)

    print(f"Showing node summary status on {network}...")
    summary = get_summary(network, container_name)
    if summary:
        print(summary)

    print("Checking existing channels...")
    existing_channels = list_channels(network, container_name)
    existing_node_ids = {channel['peer_id'] for channel in json.loads(existing_channels)['channels']}

    print("Closing channels that are not in the configuration...")
    for channel in json.loads(existing_channels)['channels']:
        if channel['peer_id'] not in node_ids:
            close_channel(channel['short_channel_id'], network, container_name)

    if input(f"Do you want to fund {number_of_channels} channels with specified amounts? (yes/no) ").strip().lower() != 'yes':
        print("Operation cancelled.")
        logging.info("Operation cancelled by user.")
        return

    for i in range(number_of_channels):
        amount = channel_funds[i]
        target_node_id = node_ids[i]
        if target_node_id in existing_node_ids:
            print(f"Channel with node {target_node_id} already exists. Skipping...")
            continue
        print(f"Funding channel {i+1} with {amount} BTC to node {target_node_id} on {network}...")
        result = fund_channel(target_node_id, amount, network, container_name)
        if result:
            print(result)
        time.sleep(10)  # Sleep to allow the channel funding to process

    print(f"Final list of funds on {network}:")
    final_funds = list_funds(network, container_name)
    if final_funds:
        print(final_funds)

    print(f"Final node summary status on {network}:")
    final_summary = get_summary(network, container_name)
    if final_summary:
        print(final_summary)

if __name__ == "__main__":
    main()
