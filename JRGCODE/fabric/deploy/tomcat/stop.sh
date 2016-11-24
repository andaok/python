#!/bin/env bash
###AUTHOR:zhangkai
###DATE:2016.10.14
#VERSION : V1.1

#check whether parameter valid, unless remind of USEAGE
TOMCAT_HOME=$1
if [ $# -ne 1 ];then
  echo "[ERROR]USEAGE:$0 TOMCAT_HOME"
  exit 1
fi

ps -ef|grep java|grep -v "grep"|grep ${TOMCAT_HOME} >/dev/null 2>&1
#check whether java process on
if (($?==0));then
  cd  ${TOMCAT_HOME}
  #use shutdown.sh
  sh bin/shutdown.sh >/dev/null 2>&1
  sleep 3

  #if java process still on , kill -15 $PID
  ps -ef|grep java|grep -v "grep"|grep ${TOMCAT_HOME} >/dev/null 2>&1
  if(($?==0)); then
    PID=`ps -ef | grep java |grep -v "grep java"|grep ${TOMCAT_HOME}|awk {'print $2'}`
    kill -15 $PID
    sleep 3

    #if java process still on , kill -9 $PID
    ps -ef|grep java|grep -v "grep"|grep ${TOMCAT_HOME} >/dev/null 2>&1
    if (($?==0));then
  	 kill -9 $PID
     sleep 3

     ps -ef|grep java|grep -v "grep"|grep ${TOMCAT_HOME} >/dev/null 2>&1
     if(($?==0)); then
       echo "[INFO]Tomcat stop fail "
     else
      echo "[INFO]Tomcat stop  succuss "
     fi
   else
      echo "[INFO]Tomcat stop  succuss "
   fi
 else
      echo "[INFO]Tomcat stop  succuss "
 fi
else
   echo "[INFO] Tomcat is already stoppd"
fi
