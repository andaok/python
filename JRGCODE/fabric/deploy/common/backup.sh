#!/bin/env /bash/sh
###AUTHOR:zhangkai
###DATE:2016.10.14
#VERSION : V1.1

dir_src=$1
dir_dest=$2
APP_NAME=$3
#check whether parameter valid, unless remind of USEAGE
if [ $# -ne 3 ];then
  echo "[ERROR]USEAGE:$0 dir_src dir_dest APP_NAME"
  exit 1
fi
    date_now=`date +'%Y%m%d-%H%M%S'`
    [ -d ~/backup ] || mkdir ~/backup 
    cp -a ${dir_src} ${dir_dest}/${APP_NAME}${date_now} 
    if(($?==0));then
       echo "[INFO]Backup ${dir_src} To ${dir_dest}/$APP_NAME${date_now} Success "
    else 
       echo"[ERROR]Backup ${dir_src} To ${dir_dest}  Fail "
       exit 1
    fi

