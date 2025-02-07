#!/bin/bash
set -e

# Configuration variables
NON_INTERACTIVE=false
ACTION=""
ENV_TYPE=""
RECONFIGURE=false
COMPOSE_FOLDER="$PWD/docker"
CONFIG_DIR="$COMPOSE_FOLDER/.env"
COMPOSE_DEV="docker-compose-dev.yml"
COMPOSE_PROD="docker-compose.yml"
DOCKER_COMPOSE=$(command -v docker-compose || echo "docker compose")

# Header
echo "🚀 Ngen Deployment Script"

cd $COMPOSE_FOLDER || { echo "❌ Error: Docker Compose folder not found. This script must be run from the project root."; exit 1; }

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
            echo "⚠️ Unknown option: $1"
            exit 1
            ;;
    esac
done

echo ""
echo "Configuration file: ${ENV_FILE:-Not set}"
echo "Docker Compose executable: $DOCKER_COMPOSE"
echo "Docker Compose folder: $COMPOSE_FOLDER"
echo ""

check_env_mode() {
    if [ -z "$ENV_TYPE" ]; then
        if [ "$NON_INTERACTIVE" = true ]; then
            echo "⚠️ Running in non-interactive mode. Please specify --dev or --prod."
            exit 1
        fi

        echo "🔹 Select the environment mode:"
        echo "    1) Development"
        echo "    2) Production"
        read -p "Enter the number of your choice: " env_choice

        case "$env_choice" in
            1) ENV_TYPE="dev" ;; 
            2) ENV_TYPE="prod" ;;
            *) echo "❌ Invalid choice. Exiting..."; exit 1 ;;
        esac
    fi

    ENV_FILE="${CONFIG_DIR}/ngen.${ENV_TYPE}.env"
    EXAMPLE_FILE="${CONFIG_DIR}/ngen.${ENV_TYPE}.env.example"
    echo "Environment selected: $ENV_TYPE"
}

configure_env_mode() {
    echo "🔄 Configuring Ngen ${ENV_TYPE} environment..."

    if [ -f "$ENV_FILE" ]; then
        echo "⚠️ Configuration file already exists: ${ENV_FILE}"
        echo "Use 'bash deploy.sh reconfigure --$ENV_TYPE' to reset the configuration."
        exit 1
    fi

    if [ ! -f "$EXAMPLE_FILE" ]; then
        echo "❌ Error: Missing example file ${EXAMPLE_FILE}. Cannot proceed."
        exit 1
    fi

    tmp_file="${ENV_FILE}.tmp"
    > "$tmp_file"

    while IFS= read -r line; do
        if [[ "$line" == \#* ]] || [[ -z "$line" ]]; then
            echo "$line"
            echo "$line" >> "$tmp_file"
            continue
        fi

        IFS='=' read -r key current_value <<< "$line"
        key=$(echo "$key" | xargs)
        current_value=$(echo "$current_value" | xargs)

        if [ "$NON_INTERACTIVE" = true ]; then
            new_value="$current_value"
        else
            read -r -p "Modify ${key}? [Current: ${current_value}] (Enter to keep): " new_value < /dev/tty
        fi

        echo "${key}=${new_value:-$current_value}" >> "$tmp_file"
    done < "$EXAMPLE_FILE"

    mv "$tmp_file" "$ENV_FILE"
    echo "✅ Configuration completed: ${ENV_FILE}"
}

stop_containers() {
    echo "🛑 Stopping all Ngen environments..."
    echo "🔹 Trying to stop development environment..."
    $DOCKER_COMPOSE -f $COMPOSE_DEV down -v || true
    echo ""
    echo "🔹 Trying to stop production environment..."
    $DOCKER_COMPOSE -f $COMPOSE_PROD down -v || true
    echo "Done."
}

start_containers() {
    echo "▶️  Starting Ngen in ${ENV_TYPE} mode..."
    if [ "$ENV_TYPE" = "dev" ]; then
        COMPOSE_FILE=$COMPOSE_DEV
        ALT_COMPOSE_FILE=$COMPOSE_PROD
        ALT_MODE="Production"
        ALT_ENV_FILE="${CONFIG_DIR}/ngen.prod.env"
    else
        COMPOSE_FILE=$COMPOSE_PROD
        ALT_COMPOSE_FILE=$COMPOSE_DEV
        ALT_MODE="Development"
        ALT_ENV_FILE="${CONFIG_DIR}/ngen.dev.env"
    fi

    echo "🔹 ${ENV_TYPE^} mode selected. Using $COMPOSE_FILE"
    
    if [ -f "$ALT_ENV_FILE" ]; then
        echo "Removing containers from ${ALT_MODE} mode to avoid conflicts..."
        $DOCKER_COMPOSE -f "$ALT_COMPOSE_FILE" down -v
    else
        echo "No environment file found for ${ALT_MODE}. Skipping container removal."
    fi

    if $DOCKER_COMPOSE -f $COMPOSE_FILE ps | grep -q 'Up'; then
        echo "⚠️  System is already running. Stop it before starting again."
        exit 1
    fi
    
    echo "Launching Ngen in ${ENV_TYPE} mode..."
    $DOCKER_COMPOSE -f $COMPOSE_FILE up -d
}

# Execution flow
if [ "$ACTION" = "stop" ]; then
    stop_containers
    
elif [ "$ACTION" = "start" ]; then
    check_env_mode

    if [ -f "$ENV_FILE" ]; then
        echo "✅ Using existing configuration file: ${ENV_FILE}"
    else
        echo "⚙️ Configuration file not found for ${ENV_TYPE}. Creating a new one..."
        configure_env_mode
    fi

    start_containers

elif [ "$ACTION" = "reconfigure" ]; then
    check_env_mode
    rm -f "$ENV_FILE"
    configure_env_mode
    echo "✅ Configuration completed: ${ENV_FILE}"
    echo "Use 'bash deploy.sh start --$ENV_TYPE' to start Ngen"
    echo "Use 'bash deploy.sh stop --$ENV_TYPE' to stop Ngen"
fi

exit 0
