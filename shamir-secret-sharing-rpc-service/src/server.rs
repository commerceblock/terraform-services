use std::{env, fs};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::Path;
use std::sync::Arc;

use bip39::Mnemonic;
use blake2::Blake2bVar;
use blake2::digest::{Update, VariableOutput};
use hex::FromHex;
use tokio::sync::Mutex;
use tonic::{transport::Server, Request, Response, Status};

use key_share::coordinator_server::{Coordinator, CoordinatorServer};
use key_share::{AddMnemonicReply, AddMnemonicRequest, KeyListReply};

const SHAMIR_SHARES: usize = 3;
const SHAMIR_THRESHOLD: usize = 2;

fn write_file_if_not_exists(path: &str, content: &str) -> bool {
    let path = Path::new(path);

    // Check if the file does not exist
    if !path.exists() {
        // Open the file in write-only mode, create it if it does not exist.
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true) // This ensures the file is created only if it does not exist
            .open(path).unwrap();

        let content = content.trim_end_matches(|c| c == '\r' || c == '\n');


        // Write the content to the file
        file.write_all(content.as_bytes()).unwrap();

        return true;
    }

    false
}

pub mod key_share {
    tonic::include_proto!("keyshare"); // The string specified here must match the proto package name
}

#[derive(Debug, Default, PartialEq)]
pub struct KeyShare {
    key_hex: String,
    index: u32,
}

#[derive(Debug, Default)]
pub struct MyCoordinator {
    key_shares: Arc<Mutex<Vec<KeyShare>>>,
}

fn xor_buffers(buf: &[u8; 32], mnemonic: &Vec<u8>) -> Result<Vec<u8>, String> {
    // Check if the size of the mnemonic is exactly 32 bytes
    if mnemonic.len() != 32 {
        return Err("mnemonic must be exactly 32 bytes".to_string());
    }

    // Perform XOR operation between the elements of the array and the vector
    let result = buf.iter()
                    .zip(mnemonic.iter())
                    .map(|(&x, &y)| x ^ y)
                    .collect::<Vec<u8>>();

    Ok(result)
}


impl MyCoordinator {

    async fn add_share(&self, key_hex: String, index: u32) -> Result<String, Status> {
        let mut shares = self.key_shares.lock().await;

        if shares.len() >= SHAMIR_SHARES {
            return Ok("Enough key shares have already been added.".to_string());
        }

        let new_key_share = KeyShare { key_hex, index };

        // Check for duplicates
        if shares.iter().any(|ks| ks.key_hex == new_key_share.key_hex || ks.index == new_key_share.index) {
            return Ok("Key already exists.".to_string());
        } else {
            shares.push(new_key_share); // Insert the new KeyShare if no duplicates are found
        }

        let mut message = "Key added successfully".to_string();

        let mut secret_shares: Vec<Vec<u8>> = Vec::new();
        let mut indexes: Vec<usize> = Vec::new();

        if shares.len() >= SHAMIR_THRESHOLD {

            for share in shares.iter() {
                let ks = hex::decode(share.key_hex.to_string()).unwrap();
                secret_shares.push(ks);
                indexes.push(share.index as usize);
            }

            let secret = bc_shamir::recover_secret(&indexes, &secret_shares).unwrap();

            let seed_content =  hex::encode(secret);

            let seed_file = get_seed_file();

            let written = write_file_if_not_exists(&seed_file, &seed_content);

            message += " and secret recovered.";

            message.push_str(if written {
                " Seed written to file."
            } else {
                " Seed file already exists."
            });
        }

        Ok(message)
    }

}

#[tonic::async_trait]
impl Coordinator for MyCoordinator {

    async fn add_mnemonic(
        &self,
        request: Request<AddMnemonicRequest>,
    ) -> Result<Response<AddMnemonicReply>, Status> {

        if check_seed_file().unwrap() {
            let message = "A valid seed file already exists. New keys will be ignored.".to_string();
            return Ok(Response::new(AddMnemonicReply { message }));
        }

        let request_inner = request.into_inner();
        let mnemonic_str = request_inner.mnemonic;
        let index = request_inner.index;
        let password = request_inner.password;

        let password = password.as_bytes();

        let mut hasher = Blake2bVar::new(32).unwrap();
        hasher.update(password);
        let mut buf = [0u8; 32];
        hasher.finalize_variable(&mut buf).unwrap();

        let mnemonic = Mnemonic::parse(&mnemonic_str).unwrap();

        let xor_result = xor_buffers(&buf, &mnemonic.to_entropy()).unwrap();

        let key_hex = hex::encode(xor_result);

        let message = self.add_share(key_hex, index).await?;

        Ok(Response::new(AddMnemonicReply { message }))
    }

    async fn list_keys(&self, _request: Request<()>) -> Result<Response<KeyListReply>, Status> {

        let mut message = KeyListReply::default();

        let shares = self.key_shares.lock().await;

        for key_share in &shares[..] {
            message.items.push(key_share.key_hex.to_string());
        }

        Ok(Response::new(message))

    }
}

fn get_seed_file() -> String {
    let seed_path = env::var("SEED_PATH").unwrap_or_else(|_| "/home/vls/.lightning-signer/bitcoin".into());
    let seed_file_name = env::var("SEED_FILE_NAME").unwrap_or_else(|_| "node.seed".into());
    format!("{}/{}", seed_path, seed_file_name)
}

fn check_seed_file() -> Result<bool, Box<dyn std::error::Error>> {
    let seed_file = get_seed_file();

    // Check if the file exists
    if !Path::new(&seed_file).exists() {
        return Ok(false);
    }

    // Read the content of the file
    let content = fs::read_to_string(&seed_file)?.trim().to_string();

    // Attempt to decode the hex string into bytes
    let is_valid_hex = match Vec::from_hex(&content) {
        Ok(bytes) => bytes.len() == 32, // Check if the decoded byte array is exactly 32 bytes long
        Err(_) => false, // If decoding fails, the hex string is not valid
    };

    if !is_valid_hex {
        // If the file content is not a valid 32-byte hex string, delete the file
        fs::remove_file(&seed_file)?;
        println!("Invalid seed file deleted.");
        return Ok(false);
    }

    Ok(true)
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {

    if check_seed_file().unwrap() {
        println!("A valid seed file already exists. The server will not start.");
        return Ok(());
    }

    // let addr = "[::1]:50051".parse()?;
    let addr = "127.0.0.1:50051".parse()?;
    let coordinator = MyCoordinator::default();

    println!("Server started at {}", addr);

    Server::builder()
        .add_service(CoordinatorServer::new(coordinator))
        .serve(addr)
        .await?;

    Ok(())
}
