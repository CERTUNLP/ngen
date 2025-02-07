#!/bin/bash
set -e

# Configuration variables
CONFIG_DIR=".env"
NON_INTERACTIVE=false
ACTION=""
ENV_TYPE=""
RECONFIGURE=false
COMPOSE_FOLDER="$PWD/docker"
COMPOSE_DEV="docker-compose-dev.yml"
COMPOSE_PROD="docker-compose.yml"
DOCKER_COMPOSE=$(command -v docker-compose || echo "docker compose")


echo "🚀 ngen deployment script"

cd $COMPOSE_FOLDER || { echo "Error: Docker Compose folder not found. This script must be run from the project root."; exit 1; }

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev|--prod)
            ENV_TYPE="${1#--}"
            shift
            ;;
        --non-interactive)
            NON_INTERACTIVE=true
            shift
            ;;
        start|stop|reconfigure)
            ACTION=$1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Configuration file: $ENV_FILE"
echo "Docker Compose executable: $DOCKER_COMPOSE"
echo "Docker Compose folder: $COMPOSE_FOLDER"


check_env_mode() {
    # Interactive environment selection if not provided
    if [ -z "$ENV_TYPE" ]; then
        if [ "$NON_INTERACTIVE" = false ]; then
            echo "Running in non-interactive mode. Use --dev or --prod to specify environment."
            echo "Exiting..."
            exit 1
        fi

        echo "Select the environment mode:"
        echo "    1) Development"
        echo "    2) Production"
        read -p "Enter the number of your choice: " env_choice

        case "$env_choice" in
            1) ENV_TYPE="dev" ;; 
            2) ENV_TYPE="prod" ;;
            *) echo "Invalid choice. Exiting..."; exit 1 ;;
        esac
    fi

    ENV_FILE="${CONFIG_DIR}/ngen.${ENV_TYPE}.env"
    EXAMPLE_FILE="${CONFIG_DIR}/ngen.${ENV_TYPE}.env.example"

    echo "Environment: $ENV_TYPE"
}

# Configure environment
configure_env_mode() {
    echo "Configuring ngen ${ENV_TYPE} environment..."

    # If configuration file is missing, create from example
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$EXAMPLE_FILE" ]; then
            cp "$EXAMPLE_FILE" "$ENV_FILE"
            echo "Created new ${ENV_TYPE} configuration from example file"
        else
            echo "Error: Missing example file ${EXAMPLE_FILE}"
            exit 1
        fi
    fi

    tmp_file="${ENV_FILE}.tmp"
    > "$tmp_file"

    while IFS= read -r line; do
        if [[ "$line" =~ ^# ]] || [[ -z "$line" ]]; then
            echo "$line" >> "$tmp_file"
            continue
        fi

        IFS='=' read -r key current_value <<< "$line"
        key=$(echo "$key" | xargs)
        current_value=$(echo "$current_value" | xargs)

        if [ "$NON_INTERACTIVE" = true ]; then
            new_value="$current_value"
        else
            read -rp "Modify ${key}? [Current: ${current_value}] (Enter to keep): " new_value
        fi

        echo "${key}=${new_value:-$current_value}" >> "$tmp_file"
    done < "$ENV_FILE"

    mv "$tmp_file" "$ENV_FILE"
}

stop_containers() {
    echo "Stopping ngen ${ENV_TYPE} environment..."
    $DOCKER_COMPOSE -f $COMPOSE_DEV -f $COMPOSE_PROD down -v
}



start_containers() {
    if [ "$ENV_TYPE" = "dev" ]; then
        COMPOSE_FILE=$COMPOSE_DEV
        ALT_COMPOSE_FILE=$COMPOSE_PROD
        ALT_MODE="Production"
    else
        COMPOSE_FILE=$COMPOSE_PROD
        ALT_COMPOSE_FILE=$COMPOSE_DEV
        ALT_MODE="Development"
    fi

    echo "⚠️  ${ENV_TYPE^} mode selected. Using $COMPOSE_FILE"
    echo "Removing containers in ${ALT_MODE} mode to avoid conflicts..."
    $DOCKER_COMPOSE -f "$ALT_COMPOSE_FILE" down -v

    if $DOCKER_COMPOSE -f $COMPOSE_FILE ps | grep -q 'Up'; then
        echo "❗  System is already running. Stop it before starting again."
        exit 1
    fi
    
    configure_env_mode
    echo "Starting ngen in ${ENV_TYPE} mode..."
    $DOCKER_COMPOSE -f $COMPOSE_FILE up -d
}

# Execution flow
if [ "$ACTION" = "stop" ]; then
    stop_containers
    
elif [ "$ACTION" = "start" ]; then
    check_env_mode

    # If already configured use existing configuration
    if [ -f "$ENV_FILE" ]; then
        echo "Using existing configuration file: ${ENV_FILE}"
    else
        echo "Configuration file not found for ${ENV_TYPE} environment. Creating new configuration..."
        configure_env_mode
    fi

    start_containers

elif [ "$ACTION" = "reconfigure" ]; then
    check_env_mode
    configure_env_mode
    echo "✅ Configuration completed: ${ENV_FILE}"
    echo "Use 'bash deploy.sh start --$ENV_TYPE' to start ngen"
    echo "Use 'bash deploy.sh stop --$ENV_TYPE' to stop ngen"
fi

exit 0
