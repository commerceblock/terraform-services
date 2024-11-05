import subprocess

# Function to execute lightning-cli commands inside the Docker container
def run_lightning_cli(command):
    docker_command = [
        "docker", "exec", "lightningd-mainnet", "lightning-cli"
    ] + command.split()

    try:
        # Execute the command and capture the output
        result = subprocess.run(docker_command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
        print("Output:", e.output)
        return None
