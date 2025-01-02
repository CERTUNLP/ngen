#!/bin/sh

# Usar envsubst para sustituir variables en la configuración de NGINX
export VITE_APP_API_SERVER=${VITE_APP_API_SERVER:-/api/}
envsubst '\$VITE_APP_API_SERVER' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Arrancar NGINX
nginx -g 'daemon off;'
