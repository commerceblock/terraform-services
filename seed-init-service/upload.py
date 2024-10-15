from flask import Flask, request, jsonify

from google.cloud import kms
from google.cloud import secretmanager
import base64

secret_uploaded = False

# Create a Flask application instance
app = Flask(__name__)

# Define a single POST route
@app.route('/uploadsecret', methods=['POST'])
def uploadsecret():
    global secret_uploaded
    # Get the JSON data from the request
    data = request.get_json()

    if secret_uploaded:
        return jsonify({"status": "existing_key"}), 409
    # Check if 'message' is in the JSON data
    if 'secret' in data:
        print("secret received")
        try:
            kms_client = kms.KeyManagementServiceClient()
            secret_manager_client = secretmanager.SecretManagerServiceClient()

            # edit to included project and KMS details
            project_id = "cb-ln-testnet-dev"
            location = "global"
            key_ring_name = "node-seed"
            key_name = "seed"

            key_path = kms_client.crypto_key_path(project_id, location, key_ring_name, key_name)
            secret_name = "node-seed"
            plaintext = data['secret']
            encrypt_response = kms_client.encrypt(
            name=key_path, plaintext=plaintext.encode("utf-8")
            )
            ciphertext = encrypt_response.ciphertext
            print("secret encrypted")
            base64_ciphertext = base64.b64encode(ciphertext).decode("utf-8")
            secret = secret_manager_client.create_secret(
                request={"parent": f"projects/{project_id}/secrets", "secret_id": secret_name}
            )
            secret_manager_client.add_secret_version(
                request={
                    "parent": secret.name,
                    "payload": {"data": base64_ciphertext.encode("utf-8")},
                }
            )
            print("secret uploaded")
            secret_uploaded = True
            return jsonify({"status": "success"}), 200
        except:
            return jsonify({"status": "failure", "error": "Upload failure"}), 400
    else:
        return jsonify({"status": "failure", "error": "Missing 'secret' key"}), 400

# Run the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
