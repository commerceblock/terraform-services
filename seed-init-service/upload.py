import logging
from flask import Flask, request, jsonify
from google.cloud import kms
from google.cloud import secretmanager
import base64

secret_uploaded = False

# Configure logging
logging.basicConfig(
    filename='~/log_file_3.log',  # Use absolute path if necessary
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create a Flask application instance
app = Flask(__name__)

# Define a single POST route
@app.route('/uploadsecret', methods=['POST'])
def uploadsecret():
    global secret_uploaded
    # Get the JSON data from the request
    data = request.get_json()

    if secret_uploaded:
        logging.warning("Attempt to upload an existing key.")
        return jsonify({"status": "existing_key"}), 409

    # Check if 'secret' is in the JSON data
    if 'secret' not in data:
        logging.error("Missing 'secret' key in the request data.")
        return jsonify({"status": "failure", "error": "Missing 'secret' key"}), 400

    logging.info("Secret received: %s", data['secret'])

    try:
        kms_client = kms.KeyManagementServiceClient()
        secret_manager_client = secretmanager.SecretManagerServiceClient()

        # Project and KMS details
        project_id = "cb-ln-testnet-dev"
        location = "global"
        key_ring_name = "node-seed"
        key_name = "seed"

        key_path = kms_client.crypto_key_path(project_id, location, key_ring_name, key_name)
        secret_name = "node-seed"
        plaintext = data['secret']

        # Encrypt the secret
        encrypt_response = kms_client.encrypt(
            name=key_path, plaintext=plaintext.encode("utf-8")
        )
        ciphertext = encrypt_response.ciphertext
        logging.info("Secret encrypted successfully.")

        # Encode the ciphertext to base64
        base64_ciphertext = base64.b64encode(ciphertext).decode("utf-8")
        
        # Create the secret in Secret Manager
        secret = secret_manager_client.create_secret(
            request={"parent": f"projects/{project_id}/secrets", "secret_id": secret_name}
        )
        logging.info("Secret created in Secret Manager.")

        # Add a new secret version
        secret_manager_client.add_secret_version(
            request={
                "parent": secret.name,
                "payload": {"data": base64_ciphertext.encode("utf-8")},
            }
        )
        logging.info("Secret version added successfully.")
        
        secret_uploaded = True
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error("Error during secret upload process: %s", str(e))
        return jsonify({"status": "failure", "error": str(e)}), 500

# Run the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
