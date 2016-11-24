#!/bin/bash

NGINX_CONF="$1"
NGINX_DAEMON="$2"
APP_HOST="$3"
APP_PORT="$4"

if [ $# -ne 4 ];then
  echo "[ERROR]USEAGE:NGINX_CONF NGINX_DAEMON APP_HOST APP_PORT "
  exit 1
fi

# nginx set application node down
grep -E "server ${APP_HOST}:${APP_PORT}" ${NGINX_CONF} >/dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "[ERROR] "${NGINX_CONF}" missing: "${APP_HOST}:${APP_PORT}""
  exit 1
elif [ "$(grep  "server ${APP_HOST}:${APP_PORT}" ${NGINX_CONF}|grep -c down)" -eq "1" ] ;then
  echo "${NGINX_CONF} already ${APP_HOST}:${APP_PORT} down"
fi
sudo sed -i -r "/(server ${APP_HOST}:${APP_PORT})/s/(\s\s*down){1,};\s*/;/" ${NGINX_CONF}
sudo sed -i -r "/(server ${APP_HOST}:${APP_PORT})/s/;/ down;/" ${NGINX_CONF}
sudo ${NGINX_DAEMON} -s reload
if [ $? -ne 0 ]; then
  echo "[ERROR] ${NGINX_DAEMON} reload fail"
  exit 1
fi