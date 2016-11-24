#!/bin/env bash

TOMCAT_HOME=$1
APP_NAME=$2
dir_update=$3

#check whether arguments valid, unless remind of USEAGE
if [ $# -ne 3 ];then
  echo "[ERROR]USEAGE:$0 TOMCAT_HOME APP_NAME dir_update"
  exit 1
fi

#check whether $dir_update empty or not
f=`ls $dir_update | wc -l`
if ((f==0));then
  echo "[ERROR]The $dir_update is empty"
  exit 1
fi

#check whether ${APP_NAME}.war exists
if [ ! -f "${dir_update}/${APP_NAME}.war" ];then
  echo "[ERROR]${APP_NAME}.war missing"
  exit 1
fi
   #full update
rm -rf ${TOMCAT_HOME}/webapps/*  && mv $dir_update/${APP_NAME}.war ${TOMCAT_HOME}/webapps/ 
  if(($?==0));then
       echo "[INFO]Full Update Success"
     else
       echo "[ERROR]Full Update Fail"  
       exit 1
  fi

