#!/bin/bash
##############################################
# Purpose:
#    Down upstream host from nginx
#
# Author: weiye
# Date  : 20160817 
############################################

upstream_host_ip=$1
upstream_app_port=$2
action_flag=$3

nginx_dir="/usr/local/nginx/"
nginx_conf_file="${nginx_dir}/conf/vhost/jenkins_test.conf"

function down_upstream_host()
{
    sed -i -r  "/(server ${upstream_host_ip}:${upstream_app_port})/s/;/ down;/"   ${nginx_conf_file}
    if [ $? -eq 0 ]; then
         ${nginx_dir}/sbin/nginx -s reload
         echo "down host ${upstream_host_ip} from nginx success!"
    fi
}

function up_upstream_host()
{
    sed -i -r  "/(server ${upstream_host_ip}:${upstream_app_port})/s/ down;/;/"   ${nginx_conf_file}
    if [ $? -eq 0 ]; then
       ${nginx_dir}/sbin/nginx -s reload
       echo "up host ${upstream_host_ip} from nginx success!"
    fi
}

case $action_flag in
     down)
     down_upstream_host
     ;;
     up)
     up_upstream_host
     ;;
     *)
     echo "UNKNOWN ARG,QUIT"
     exit 1
     ;;
esac

exit 0

