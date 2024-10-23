import json
import subprocess

# Load config from file
with open('config.json', 'r') as file:
    config = json.load(file)

lightning_config = config['lightning']
channels = config['channels']

# Execute commands in the lightningd container
def run_lightning_command(command):
    container_name = lightning_config['container_name']
    full_command = ['docker', 'container', 'exec', container_name] + command
    result = subprocess.run(full_command, capture_output=True, text=True)
    
    if result.returncode == 0:
        return result.stdout.strip()  # Return the command output
    else:
        raise Exception(f"Command failed: {result.stderr.strip()}")

# Get the list of currently open channels from the lightning node
def get_open_channels():
    try:
        response = run_lightning_command(['lightning-cli', 'listpeers'])
        peers_info = json.loads(response)
        open_channels = []
        
        for peer in peers_info['peers']:
            for channel in peer['channels']:
                if channel['state'] == 'CHANNELD_NORMAL':  # Active/open channel
                    open_channels.append({
                        'node_id': peer['id'],
                        'funds': channel['msatoshi_total'] / 1e8  # Convert msat to BTC
                    })
        return open_channels
    except Exception as e:
        raise Exception(f"Failed to list open channels: {e}")

# Close a channel if it's not supposed to be open
def close_channel(node_id):
    try:
        run_lightning_command(['lightning-cli', 'close', node_id])
        print(f"Closed channel with {node_id}")
    except Exception as e:
        print(f"Error closing channel with {node_id}: {e}")

# Open a new channel if it's missing
def open_channel(node_id, funds):
    try:
        response = run_lightning_command(['lightning-cli', 'fundchannel', node_id, str(funds)])
        print(f"Opened channel with {node_id} for {funds} BTC: {response}")
    except Exception as e:
        print(f"Error opening channel with {node_id}: {e}")

def manage_channels():
    try:
        open_channels = get_open_channels()
        print(f"Currently open channels: {open_channels}")

        # Channels in config that should be open
        config_channels = [{'node_id': c['node_id'], 'funds': float(c['funds'])} for c in channels]

        # Close extra channels that aren't in the config
        for open_channel in open_channels:
            if open_channel not in config_channels:
                print(f"Channel with {open_channel['node_id']} is open but not in the config, closing it.")
                close_channel(open_channel['node_id'])

        # Open missing channels
        for config_channel in config_channels:
            if config_channel not in open_channels:
                print(f"Channel with {config_channel['node_id']} is not open, opening it.")
                open_channel(config_channel['node_id'], config_channel['funds'])

    except Exception as e:
        print(f"Error managing channels: {e}")

def main():
    manage_channels()

if __name__ == '__main__':
    main()
