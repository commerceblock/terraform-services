from google.cloud import kms
from google.cloud import secretmanager
import base64

# Set up KMS client
kms_client = kms.KeyManagementServiceClient()

# Set up Secrets Manager client
secret_manager_client = secretmanager.SecretManagerServiceClient()

# Replace with your project ID, location, key ring, and key name
project_id = "cb-ln-testnet-dev"
location = "global"
key_ring_name = "node-seed"
key_name = "seed"

# Construct the key path
key_path = kms_client.crypto_key_path(project_id, location, key_ring_name, key_name)

# Replace with your secret name
secret_name = "node-seed"

# Get the latest secret version
secret = secret_manager_client.get_secret(request={"name": f"projects/{project_id}/secrets/{secret_name}"})
secret_version = secret_manager_client.access_secret_version(request={"name": secret.versions[0].name})

# Decode the base64-encoded ciphertext
ciphertext = base64.b64decode(secret_version.payload.data)

# Decrypt the string using KMS
decrypt_response = kms_client.decrypt(name=key_path, ciphertext=ciphertext)
plaintext = decrypt_response.plaintext.decode("utf-8")

# Save the decrypted string to a file
with open("node.seed", "w") as f:
    f.write(plaintext)

print(f"Decrypted string saved to file: decrypted_string.txt")
