use key_share::coordinator_client::CoordinatorClient;

use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
#[command(propagate_version = true)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Add a key share to the Shamir Secret Sharing scheme
    AddMnemonic { mnemonic: String, password: String, index: u32 },
}

pub mod key_share {
    tonic::include_proto!("keyshare");
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
     // let mut client = CoordinatorClient::connect("http://[::1]:50051").await?;
     let mut client = CoordinatorClient::connect("http://127.0.0.1:50051").await?;

    let cli = Cli::parse();

    match cli.command {
        Commands::AddMnemonic { mnemonic, password, index } => {
            let request = tonic::Request::new(key_share::AddMnemonicRequest {
                mnemonic,
                password,
                index
            });

            let response = client.add_mnemonic(request).await?;

            println!("RESPONSE={:?}", response);
        },
    }

    Ok(())
}