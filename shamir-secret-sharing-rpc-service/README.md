# Shamir Secret Sharing RPC

# Running from source

`sudo apt-get install -y protobuf-compiler libprotobuf-dev` before running.

`export SEED_PATH=<folder_to_write_seed_file> && cargo run --bin keyshare-server` to start the server.

`cargo run --bin keyshare-client add-mnemonic "fork clerk hover mystery replace crucial industry deliver rule into broom brave derive slam limit market alarm weird worth reform idle indoor ozone must" tdgjhwJ75KnA 0`  to add a mnemonic.

The command is `cargo run --bin keyshare-client add-key-share <mnemonic> <password> <index>`.

# Running from Dockerfile

`docker build -t keyshare .` to build the image.

`docker run -d --name keyshare-server -v /home/<user>:/home/vls/.lightning-signer/bitcoin -p 50051:50051 keyshare` to run the container

`docker exec keyshare-server keyshare-client add-mnemonic "fork clerk hover mystery replace crucial industry deliver rule into broom brave derive slam limit market alarm weird worth reform idle indoor ozone must" tdgjhwJ75KnA 0` to send a mnemonic.
