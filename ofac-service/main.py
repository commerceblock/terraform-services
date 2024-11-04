import address_update
import check_utxos
import check_ips
from lightning import run_lightning_cli

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
