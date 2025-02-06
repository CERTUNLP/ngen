#!/bin/bash

set -e  # Stop execution on error

# Variables
git_repo="https://github.com/CERTUNLP/ngen.git"
install_dir="$HOME/ngen"
docker_dir="$install_dir/docker"

echo "[+] Installing necessary dependencies..."
# Check if Docker is installed, if not, install it
docker --version &> /dev/null || {
    echo "[+] Installing Docker..."
    sudo apt update && sudo apt install -y docker.io
    sudo systemctl enable --now docker
}

# Check if Docker Compose is installed, if not, install it
docker compose version &> /dev/null || {
    echo "[+] Installing Docker Compose..."
    sudo apt install -y docker-compose
}

# Clone the repository if it does not exist
if [ ! -d "$install_dir" ]; then
    echo "[+] Cloning ngen repository..."
    git clone "$git_repo" "$install_dir"
else
    echo "[+] Updating existing ngen..."
    cd "$install_dir"
    git pull
fi

# Move to the installation directory
cd "$docker_dir"

# Ask the user which environment to use
echo "[?] Select the environment mode:"
echo "    1) Production"
echo "    2) Development"
read -p "[>] Enter the number of your choice: " env_choice

if [ "$env_choice" == "1" ]; then
    echo "[+] Setting up production environment..."
    # Stop development containers if running
    docker compose -f docker-compose-dev.yml down || true
    
    # Configure environment variables
    env_file="$docker_dir/ngen.prod.env"
    example_env_file="$docker_dir/ngen.prod.env.example"
    
    if [ -f "$example_env_file" ]; then
        echo "[+] Configuring production environment variables..."
        cp "$example_env_file" "$env_file"
        while IFS='=' read -r key value; do
            if [[ ! -z "$key" && "$key" != "#"* ]]; then
                read -p "[?] Set value for $key (default: $value): " user_value
                echo "$key=${user_value:-$value}" >> "$env_file"
            fi
        done < "$example_env_file"
    fi
    
    # Start production containers
    docker compose -f docker-compose.yml up -d --build

elif [ "$env_choice" == "2" ]; then
    echo "[+] Setting up development environment..."
    # Stop production containers if running
    docker compose -f docker-compose.yml down || true
    
    # Start development containers
    docker compose -f docker-compose-dev.yml up -d --build
else
    echo "[!] Invalid choice. Exiting..."
    exit 1
fi

echo "[+] Installation and deployment completed."
echo "[+] You can access ngen in your browser once the services are ready."
