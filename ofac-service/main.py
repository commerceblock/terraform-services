import configparser
import os
import subprocess
import address_update
import check_utxos
import check_ips

# Function to execute lightning-cli commands inside the Docker container
def run_lightning_cli(command):
    docker_command = [
        "docker", "exec", "lightningd-mainnet", "lightning-cli"
    ] + command.split()

    try:
        # Execute the command and capture the output
        result = subprocess.run(docker_command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
        print("Output:", e.output)
        return None

# Checks if the Lightning RPC connection (through Docker exec) is working
def check_lightning_cli():
    try:
        output = run_lightning_cli("listpeers")
        if output:
            print("Connection to lightning-cli is successful.")
            return True
        return False
    except Exception as e:
        print("Error connecting to lightning-cli:", e)
        return False

# Main program execution
def main():
    address_update.execute()
    check_utxos.execute()
    check_ips.execute()

if __name__ == "__main__":
    if check_lightning_cli():
        main()
    else:
        print("Failed to initialize or connect to Lightning RPC.")
