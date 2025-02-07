#!/bin/sh

# Usar envsubst para sustituir variables en la configuración de NGINX
export VITE_APP_API_HOST=${VITE_APP_API_HOST}
export VITE_APP_API_PORT=${VITE_APP_API_PORT}
export VITE_APP_API_PATH=${VITE_APP_API_PATH}
envsubst '${VITE_APP_API_HOST} ${VITE_APP_API_PORT} ${VITE_APP_API_PATH}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Arrancar NGINX
nginx -g 'daemon off;'
