#!/bin/sh

# Use envsubst to substitute variables in the NGINX configuration
export VITE_APP_API_HOST=${VITE_APP_API_HOST}
export VITE_APP_API_PORT=${VITE_APP_API_PORT}
export VITE_APP_API_PATH=${VITE_APP_API_PATH}

# Check if SSL is enabled
if [ "$SSL" = "0" ] || [ "$SSL" = "false" ] || [ "$SSL" = "FALSE" ] || [ "$SSL" = "False" ] || [ "$SSL" = "F" ]; then
    echo "Configuring NGINX without SSL (port 80)..."
    envsubst '${VITE_APP_API_HOST} ${VITE_APP_API_PORT} ${VITE_APP_API_PATH}' < /etc/nginx/nginx.conf.template.no-ssl > /etc/nginx/nginx.conf
else
    echo "Configuring NGINX with SSL (port 443)..."
    envsubst '${VITE_APP_API_HOST} ${VITE_APP_API_PORT} ${VITE_APP_API_PATH}' < /etc/nginx/nginx.conf.template.ssl > /etc/nginx/nginx.conf
fi

# Start NGINX
nginx -g 'daemon off;'
