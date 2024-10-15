# node.seed initialisation scripts

## Upload

0. Configure `upload.py` with `project-id` and KMS and secrets manager paths and names. 

1. Provision a temporary confidential VM (call this the 'key-init' VM).
2. Run the upload server: `nohup python server.py &` which starts the server on port localhost:5000
3. Install and run the keyshare-server container.
4. Enter shares into the keyshare-server container.
5. Server will receive secret (on endpoint `/uploadsecret`, encrypt and upload. 
6. Destroy 'key-init' VM.

## Download

On vls startup procedure:

0. Configure `download.py` with `project-id` and KMS and secrets manager paths and names. 

1. Create ram drive partition and symbolic link:

```
mkdir -p /media/nameme
mount -t tmpfs -o size=256M tmpfs /media/nameme/
```

2. Run python script to pull node.seed from secrets manager and decrypt with KMS. Save to ram drive.
3. Start vls container. 
4. Destroy ram drive.

Need to set-up IAM policy to: only enable access to the specified KMS from the key-init and vls confidential VMs.
Any additional deployment of key-init and vls confidential VMs requires two users to agree.


To set up KMS and Secrets Manager on Google Cloud:

1. Enable the APIs

KMS:
Go to the Google Cloud Console: https://console.cloud.google.com/
Navigate to "APIs & Services" -> "Library"
Search for "Cloud Key Management Service API" and enable it.
Secrets Manager:
In the same "APIs & Services" -> "Library" section, search for "Secret Manager API" and enable it.
2. Create a KMS Key Ring and Key

Key Ring:
In the Cloud Console, go to "Key Management" -> "Key Rings"
Click "Create Key Ring"
Choose a location (e.g., "us-central1") and a name for your key ring.
Key:
Within the key ring, click "Create Crypto Key"
Choose a name for your key.
Select the "Cryptographic Algorithm" (e.g., "Google Symmetric Encryption" for general-purpose encryption).
You can optionally set a rotation period for the key.
3. Create a Secrets Manager Secret

Secret:
In the Cloud Console, go to "Secret Manager" -> "Secrets"
Click "Create Secret"
Choose a name for your secret.
Select a location (e.g., "us-central1").
You can optionally set a rotation period for the secret.
4. Grant Permissions

KMS:
If you're using a service account to interact with KMS, grant it the "Cloud KMS CryptoKey Encrypter/Decrypter" role.
Secrets Manager:
Grant the service account the "Secret Manager Secret Accessor" role to allow it to read and write secrets.
