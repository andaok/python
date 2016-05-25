#!/bin/bash

scriptroot=$(cd $(dirname $0); pwd)
source $scriptroot/config

cid=$1
rootdir=/Data

#mysql -u $user -D $database -h $host --password=$password -e "select unit_code from t_region where index_code='$cid'" 
oid=$(mysql -u $user -D $database -h $host --password=$password -e "select unit_code from t_device where index_code='$cid'"  | sed '1d') 
if [ "X$oid" == "X" ]; then
    exit 301
fi

mkdir -p $rootdir/$oid/$cid/media
echo $cid >> $scriptroot/vodconfig
mysql -u $user -D $database -h $host --password=$password -e "update t_device set status=0 where index_code='$cid'" 
if [ $? != 0 ]; then
    exit 302
fi
