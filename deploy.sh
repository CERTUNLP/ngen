#!/bin/bash
set -e

# Configuration variables
CONFIG_DIR=".env"
NON_INTERACTIVE=false
ACTION=""
ENV_TYPE=""
RECONFIGURE=false

cd docker || exit

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
        --reconfigure)
            RECONFIGURE=true
            shift
            ;;
        start|stop)
            ACTION=$1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            do_exit 1
            ;;
    esac
done

# Interactive environment selection if not provided
if [ -z "$ENV_TYPE" ]; then
    if [ "$NON_INTERACTIVE" = false ]; then
        echo "Running in non-interactive mode. Use --dev or --prod to specify environment."
        echo "Exiting..."
        do_exit 1
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

DOCKER_COMPOSE=$(command -v docker-compose || echo "docker compose")

echo "Environment: $ENV_TYPE"
echo "Configuration file: $ENV_FILE"

# Configure environment
configure_environment() {
    # If already configured and non-interactive, skip
    if [ -f "$ENV_FILE" ] && [ "$NON_INTERACTIVE" = true ] && [ "$RECONFIGURE" = false ]; then
        echo "Using existing configuration file: ${ENV_FILE}"
        return
    fi

    # If configuration file is missing, create from example
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$EXAMPLE_FILE" ]; then
            cp "$EXAMPLE_FILE" "$ENV_FILE"
            echo "Created new ${ENV_TYPE} configuration from example file"
        else
            echo "Error: Missing example file ${EXAMPLE_FILE}"
            do_exit 1
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

do_exit() {
    echo "Exiting..."
    cd ..
    exit $1
}

# Manage containers
manage_containers() {
    if [ "$ENV_TYPE" = "dev" ]; then
        COMPOSE_FILE="docker-compose-dev.yml"
        ALT_COMPOSE_FILE="docker-compose.yml"
        ALT_MODE="Production"
    else
        COMPOSE_FILE="docker-compose.yml"
        ALT_COMPOSE_FILE="docker-compose-dev.yml"
        ALT_MODE="Development"
    fi
    
    case "$ACTION" in
        start)
            echo "⚠️  ${ENV_TYPE^} mode selected. Using $COMPOSE_FILE"
            echo "Removing containers in ${ALT_MODE} mode to avoid conflicts..."
            $DOCKER_COMPOSE -f "$ALT_COMPOSE_FILE" down -v

            if $DOCKER_COMPOSE -f $COMPOSE_FILE ps | grep -q 'Up'; then
                echo "❗  System is already running. Stop it before starting again."
                do_exit 1
            fi
            
            configure_environment
            echo "Starting ngen in ${ENV_TYPE} mode..."
            $DOCKER_COMPOSE -f $COMPOSE_FILE up -d
            ;;
        stop)
            echo "Stopping ngen ${ENV_TYPE} environment..."
            $DOCKER_COMPOSE -f $COMPOSE_FILE -f $ALT_COMPOSE_FILE  down -v
            ;;
        *)
            echo "Invalid action. Use 'start' or 'stop'."
            do_exit 1
            ;;
    esac
}

# Execution flow
if [ -n "$ACTION" ]; then
    if [ "$ACTION" = "start" ]; then
        configure_environment
    fi
    manage_containers
else
    configure_environment
    echo "✅ Configuration completed: ${ENV_FILE}"
    echo "Use 'bash deploy.sh start --$ENV_TYPE' to start ngen"
    echo "Use 'bash deploy.sh stop --$ENV_TYPE' to stop ngen"
fi

do_exit 0
