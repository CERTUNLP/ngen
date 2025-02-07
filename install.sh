#!/bin/bash
set -e

# Default configuration
DEFAULT_INSTALL_DIR="${HOME}/ngen"
DEFAULT_BRANCH="main"
NON_INTERACTIVE="${NGEN_NON_INTERACTIVE:-false}"

# Command line arguments parsing
while [[ $# -gt 0 ]]; do
    case $1 in
        --install-dir)
            NGEN_INSTALL_DIR="$2"
            shift 2
            ;;
        --branch)
            NGEN_BRANCH="$2"
            shift 2
            ;;
        --non-interactive)
            NON_INTERACTIVE="true"
            shift
            ;;
            # get prod or dev
        --dev|--prod)
            ENV_TYPE="${1#--}"
            shift
            ;;
        --help)
            echo "Usage: $(basename "$0") [OPTIONS]"
            echo "Install ngen project with interactive configuration"
            echo
            echo "Options:"
            echo "  --install-dir PATH    Set installation directory"
            echo "  --branch NAME         Specify git branch"
            echo "  --non-interactive     Disable interactive prompts"
            echo "  --help                Show this help message"
            echo
            echo "Environment variables:"
            echo "  NGEN_INSTALL_DIR      Set installation directory"
            echo "  NGEN_BRANCH           Specify git branch"
            echo "  NGEN_NON_INTERACTIVE  Set to 'true' for non-interactive mode"
            exit 0
            ;;
        *)
            echo "Error: Unknown option $1"
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

# Interactive prompts
get_install_dir() {
    if [ -z "${NGEN_INSTALL_DIR}" ]; then
        if [ "${NON_INTERACTIVE}" = "true" ]; then
            NGEN_INSTALL_DIR="${DEFAULT_INSTALL_DIR}"
        else
            read -rp "Enter installation directory [${DEFAULT_INSTALL_DIR}]: " input_dir
            NGEN_INSTALL_DIR="${input_dir:-${DEFAULT_INSTALL_DIR}}"
        fi
    fi
}

get_branch() {
    if [ -z "${NGEN_BRANCH}" ]; then
        if [ "${NON_INTERACTIVE}" = "true" ]; then
            NGEN_BRANCH="${DEFAULT_BRANCH}"
        else
            read -rp "Enter git branch to use [${DEFAULT_BRANCH}]: " input_branch
            NGEN_BRANCH="${input_branch:-${DEFAULT_BRANCH}}"
        fi
    fi
}

# Validate installation directory
validate_install_dir() {
    local dir="$1"
    
    if [ -d "${dir}" ]; then
        if [ -n "$(ls -A "${dir}" 2>/dev/null)" ]; then
            if [ ! -d "${dir}/.git" ]; then
                if [ "${NON_INTERACTIVE}" = "true" ]; then
                    echo "Error: Installation directory exists and is not empty: ${dir}"
                    exit 1
                else
                    read -rp "Directory ${dir} exists and is not empty. Overwrite? [y/N] " response
                    if [[ ! "${response}" =~ ^[Yy] ]]; then
                        echo "Installation aborted"
                        exit 0
                    fi
                    rm -rf "${dir}"
                fi
            fi
        fi
    else
        mkdir -p "${dir}" || {
            echo "Error: Failed to create installation directory"
            exit 1
        }
    fi
}

# Main installation process
setup_installation() {
    get_install_dir
    get_branch
    validate_install_dir "${NGEN_INSTALL_DIR}"

    echo "Installing ngen to: ${NGEN_INSTALL_DIR}"
    echo "Using branch: ${NGEN_BRANCH}"

    if [ -d "${NGEN_INSTALL_DIR}/.git" ]; then
        echo "Updating existing repository..."
        git -C "${NGEN_INSTALL_DIR}" fetch origin
        git -C "${NGEN_INSTALL_DIR}" checkout "${NGEN_BRANCH}"
        git -C "${NGEN_INSTALL_DIR}" pull origin "${NGEN_BRANCH}"
    else
        echo "Cloning repository..."
        git clone --branch "${NGEN_BRANCH}" \
            https://github.com/CERTUNLP/ngen.git \
            "${NGEN_INSTALL_DIR}"
    fi

    echo "Installation completed successfully"
}

# Execute installation
setup_installation

# Run deploy script
nonint=""
if [ "${NON_INTERACTIVE}" = "true" ]; then
    nonint="--non-interactive"
fi
echo "Running deployment script as: bash deploy.sh start ${ENV_TYPE:+--$ENV_TYPE} ${nonint}"
cd "${NGEN_INSTALL_DIR}" && bash deploy.sh start ${ENV_TYPE:+--$ENV_TYPE} ${nonint}
