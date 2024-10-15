import address_update
import check_utxos
import check_ips

# Define rune as a global variable
rune = ""

def ask_for_rune():
    global rune
    rune_value = input("Please enter the rune value: ")
    rune= rune_value

def main():
    # Ask for the rune value before executing the other functions
    ask_for_rune()
    address_update.execute()
    check_utxos.execute()
    check_ips.execute()

if __name__ == "__main__":
    main()
