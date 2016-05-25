#!/bin/bash

cid=$1
scriptroot=$(cd $(dirname $0); pwd)
source $scriptroot/config

oid=$(mysql -u $user -D $database -h $host --password=$password -e "select status from t_device where index_code='$cid'" | sed '1d')
if [ "X$oid" == "X" ]; then
    exit 302
fi

kill -9 $(ps -ef | grep ffstart | grep $cid | grep -v grep | awk '{ print $2 }') > /dev/null
kill -9 $(ps -ef | grep ffmpeg | grep $cid | grep -v grep | awk '{ print $2 }') > /dev/null
rm -rf /Data/$oid/$cid
sed -i "/$cid/d" $scriptroot/vodconfig
