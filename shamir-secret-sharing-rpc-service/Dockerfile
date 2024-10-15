# Use a base image that has the required GLIBC version
FROM debian:bullseye-slim as builder

# Install Rust, protobuf compiler, and library dependencies
RUN apt-get update && apt-get install -y curl build-essential protobuf-compiler libprotobuf-dev pkg-config libssl-dev
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Set the environment path for Rust
ENV PATH="/root/.cargo/bin:${PATH}"

# Create a working directory
WORKDIR /usr/src/sss_rpc

# Copy your Rust project's manifests into the container
COPY ./Cargo.lock ./Cargo.lock
COPY ./Cargo.toml ./Cargo.toml

# Copy the source code of your Rust project into the container
COPY ./src ./src
COPY ./proto ./proto
COPY ./build.rs ./build.rs

# Build your Rust project. Since the source files are now present,
# the Rust compiler should be able to find and compile them.
RUN cargo build --release

# Use a Debian Slim image for the final stage to reduce the size of the final image
FROM debian:bullseye-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y protobuf-compiler libprotobuf-dev && rm -rf /var/lib/apt/lists/*

# Copy the compiled binaries from the builder stage to the final image
COPY --from=builder /usr/src/sss_rpc/target/release/keyshare-server /usr/local/bin/keyshare-server
COPY --from=builder /usr/src/sss_rpc/target/release/keyshare-client /usr/local/bin/keyshare-client

# Set the environment variables for the seed file's path
ENV SEED_PATH="/home/vls/.lightning-signer/bitcoin"
ENV SEED_FILE_NAME="node.seed"

# Create the directory and file for the SEED_FILE. You might want to ensure
# the file is writable or has specific content as needed.
RUN mkdir -p $SEED_PATH \
    && touch $SEED_PATH/$SEED_FILE_NAME

# Expose the port your server listens on if necessary
EXPOSE 50051

# Volume to persist data and access SEED_FILE
VOLUME ["/home/vls/.lightning-signer/bitcoin"]

# Command to run the server by default when the container starts
CMD ["keyshare-server"]
