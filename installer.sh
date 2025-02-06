#!/bin/bash

set -e  # Stop execution on error

# Variables
git_repo="https://github.com/CERTUNLP/ngen.git"
install_dir="$HOME/ngen"
branch="feature/Refactor_develop_and_production_environment_configuration"
docker_dir="$install_dir/docker"
env_choice=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prod|--production)
            env_choice="1"
            shift
            ;;
        --dev|--development)
            env_choice="2"
            shift
            ;;
        --help)
            echo "Usage: $0 [--prod|--dev|--help]"
            echo "  --prod, --production    Setup production environment"
            echo "  --dev, --development    Setup development environment"
            echo "  --help                  Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Docker checks
if ! command_exists docker; then
    echo "[!] Docker is not installed. Please install Docker before running this script. See https://docs.docker.com/get-docker/ for instructions."
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "[!] If Docker is already installed, make sure the Docker daemon is running and the current user is added to the 'docker' group."
    exit 1
fi

# Docker Compose checks
if ! command_exists docker-compose && ! docker compose version &> /dev/null; then
    echo "[!] Docker Compose is not installed. Please install Docker Compose before running this script. See https://docs.docker.com/compose/install/ for instructions."
    exit 1
fi

echo "[+] Docker and Docker Compose are installed."

# Clone/update repository
echo "[+] Using the following configuration:"
echo "    - Git repository: $git_repo"
echo "    - Branch: $branch"
echo "    - Installation directory: $install_dir"

if [ ! -d "$install_dir" ]; then
    echo "[+] Cloning ngen repository..."
    git clone -b "$branch" "$git_repo" "$install_dir"
else
    echo "[+] Updating existing ngen..."
    cd "$install_dir"
    git pull origin "$branch"
fi

cd "$docker_dir"

# Environment selection
if [ -z "$env_choice" ]; then
    echo "[?] Select the environment mode:"
    echo "    1) Production"
    echo "    2) Development"
    read -p "[>] Enter the number of your choice: " env_choice
fi

case "$env_choice" in
    "1"|--prod|--production)
        echo "[+] Setting up production environment..."
        docker compose -f docker-compose-dev.yml down || true
        
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
        
        docker compose -f docker-compose.yml up -d --build
        ;;

    "2"|--dev|--development)
        echo "[+] Setting up development environment..."
        docker compose -f docker-compose.yml down || true
        docker compose -f docker-compose-dev.yml up -d --build
        ;;

    *)
        echo "[!] Invalid choice. Exiting..."
        exit 1
        ;;
esac

echo "[+] Installation and deployment completed."
echo "[+] You can access ngen in your browser once the services are ready."
