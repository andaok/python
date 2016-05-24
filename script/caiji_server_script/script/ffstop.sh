#!/bin/bash

scriptroot=$(cd $(dirname $0); pwd)
source $scriptroot/config
cid=$1

mysql -u $user -D $database -h $host --password=$password -e "select status from t_device where index_code='$cid'"
if [ $? != 0 ]; then
    exit 301
fi

kill -9 $(ps -ef | grep ffstart | grep $cid | grep -v grep | awk '{ print $2 }') > /dev/null
kill -9 $(ps -ef | grep ffmpeg | grep $cid | grep -v grep | awk '{ print $2 }') > /dev/null

mysql -u $user -D $database -h $host --password=$password -e "update t_device set status=0 where index_code='$cid'"
if [ $? != 0 ]; then
    exit 302
fi


#DELETE CAMERA STATUS KEY IN REDIS POOL

redis-cli -h 10.2.10.19 -p 6379  del $cid"_status" 
redis-cli -h 10.2.10.19 -p 6379  zrem "DownCamSet" $cid
