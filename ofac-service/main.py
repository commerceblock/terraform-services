import configparser
import os
from pyln.client import LightningRpc, RpcError
import address_update
import check_utxos
import check_ips

# Read configuration from the INI file
config = configparser.ConfigParser()
config.read('config.ini')

# Initialize the LightningRpc instance
def initialize_lightning_cli():
    try:
        rpc_path = os.path.expanduser(config['lightning']['rpc_path'])
        print('Trying to find LightningRPC at:', rpc_path)
        lightningCli = LightningRpc(rpc_path)
        print('RPC Set was:', rpc_path)
        return lightningCli
    except KeyError:
        print("Error: Missing 'rpc_path' in the config file.")
    except Exception as e:
        print("Error initializing LightningRpc:", e)
    return None

# Checks if the Lightning RPC connection is working
def check_lightning_cli(lightningCli):
    try:
        lightningCli.listpeers()
        return True
    except RpcError as e:
        print("Error connecting to lightning-cli:", e)
        return False

# Main program execution
def main(lightningCli):
    address_update.execute(lightningCli)
    check_utxos.execute(lightningCli)
    check_ips.execute(lightningCli)

if __name__ == "__main__":
    lightningCli = initialize_lightning_cli()
    if lightningCli and check_lightning_cli(lightningCli):
        main(lightningCli)
    else:
        print("Failed to initialize or connect to Lightning RPC.")
