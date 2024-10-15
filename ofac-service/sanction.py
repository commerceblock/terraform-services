import bdkpython as bdk

def get_wpkh_address(public_key):

    descriptor_text = "wpkh(%s)" % (public_key)

    descriptor = bdk.Descriptor(descriptor_text, bdk.Network.BITCOIN)
    db_config = bdk.DatabaseConfig.MEMORY()

    wallet = bdk.Wallet(
             descriptor=descriptor,
             change_descriptor=None,
             network=bdk.Network.BITCOIN,
             database_config=db_config,
         )
    
    address_info = wallet.get_address(bdk.AddressIndex.LAST_UNUSED())
    address = address_info.address.as_string()
    # index = address_info.index
    # print(f"New BIP84 testnet address: {address} at index {index}")
    return address

def is_sanctioned_address(public_key):
    address = get_wpkh_address(public_key)

    if public_key == "0396c44740cf9aaf5fe82a4b571623484bc8a2f92afd608bd4f268521e0a0db0e1":
        print(f"Address: {address}")

    sanctioned_addresses = set()
    with open('sanctioned_addresses_XBT.txt', 'r') as file:
        sanctioned_addresses = set(line.strip() for line in file)

    is_sanctioned = address in sanctioned_addresses
    
    return is_sanctioned

if __name__ == "__main__":
    is_sanctioned_address("03d89f813bf631c91e3073e21827fa7cb562ca52b4aa05ffbeeda7e77ec28cd2e9")
