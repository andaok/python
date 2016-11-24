#!/bin/env bash
###AUTHOR:zhangkai
###DATE:2016.9.8
#VERSION : V1.1
#This version o support add-on and full application
#autolly place property files

TOMCAT_HOME=$1
#check whether parameter valid, unless remind of USEAGE
if [ $# -ne 1 ];then
   echo "[ERROR]USEAGE:$0 TOMECAT_HOME"
   exit 1
fi
#start up the process
ps -ef|grep java|grep $TOMCAT_HOME > /dev/null 
if [ $? -ne 0 ]; then
  cd ${TOMCAT_HOME} && sh ./bin/startup.sh
  sleep 5
  ps -ef|grep java|grep ${TOMCAT_HOME} > /dev/null 
  if [ $? -ne 0 ]; then
    echo "[ERROR]Tomcat Start Fail"
    exit 1
  else 
    echo "[INFO]Tomcat Start Success" 
  fi
else
   echo "[INFO]Tomcat Already Running"
fi


