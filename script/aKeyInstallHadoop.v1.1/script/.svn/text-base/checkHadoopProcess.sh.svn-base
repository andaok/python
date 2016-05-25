#!/bin/bash
#################################################
# Purpose:
#       monitor hadoop each node related process,
#+      write error log to syslog.if it detects a node
#+      related process not started,start that process
#+      write logs to syslog
#
# Write by wye in 20120628
# Copyright@2012 cloudiya technology
#################################################
RELDIR=`dirname $0`
ABSDIR=`cd $RELDIR;pwd`

##CONFFILEPATHFLAG##
#source checkHadoopProcess.conf
############################
#STATIC VARIABLES
CHECKSLEEPTIME=300
STARTSLEEPTIME=60
STARTCOUNT=4
############################
#SOFTWARE PATH
JDK=$HADOOPINSTALLDIR/jdk
HADOOP=$HADOOPINSTALLDIR/hadoop
############################
#SYSTEM COMMAND
LOGGER="/usr/bin/logger -i -t hadoop"
CAT=/bin/cat
ECHO=/bin/echo
PING=/bin/ping
IFCONFIG=/sbin/ifconfig
GREP=/bin/grep
AWK=/bin/awk
TR=/usr/bin/tr
SUDO=/usr/bin/sudo
SSH=/usr/bin/ssh
############################
#CHECK NAMENODE PROCESS
############################
function checknamenode()
  {
    LOOP="YES"
    STARTNNCOUNT=1
    while [ "$LOOP" == "YES" ]
    do
       if [ "X$($SUDO -u $HADOOPUSERNAME $JDK/bin/jps | $AWK '{print $2}' | grep -i namenode)" == "X" ]; then
          $LOGGER "ERROR -- $NAMENODE namenode process does not start,restart it in $STARTNNCOUNT times."
          $SUDO -u $HADOOPUSERNAME $HADOOP/bin/hadoop-daemon.sh start namenode > /dev/null 2>&1
          let STARTNNCOUNT=STARTNNCOUNT+1
          if [ "$STARTNNCOUNT" -eq "$STARTCOUNT" ]; then
             $LOGGER "ERROR -- $NAMENODE namenode process be to start $STARTNNCOUNT times,but it still does not start"
             LOOP="NO"
          fi
          sleep $STARTSLEEPTIME
       else
          $LOGGER "INFO -- $NAMENODE namenode process running normal"
          LOOP="NO"
       fi
    done 
  }
############################
#CHECK JOBTRACKER PROCESS
############################
function checkjobtracker()
  {
    LOOP="YES"
    STARTNNCOUNT=1
    while [ "$LOOP" == "YES" ]
    do
       if [ "X$($SUDO -u $HADOOPUSERNAME $JDK/bin/jps | $AWK '{print $2}' | grep -i jobtracker)" == "X" ]; then
          $LOGGER "ERROR -- $NAMENODE jobtracker process does not start,restart it in $STARTNNCOUNT times."
          $SUDO -u $HADOOPUSERNAME $HADOOP/bin/hadoop-daemon.sh start jobtracker > /dev/null 2>&1
          let STARTNNCOUNT=STARTNNCOUNT+1
          if [ "$STARTNNCOUNT" -eq "$STARTCOUNT" ]; then
             $LOGGER "ERROR -- $NAMENODE jobtracker process be to start $STARTNNCOUNT times,but it still does not start"
             LOOP="NO"
          fi
          sleep $STARTSLEEPTIME
       else
          $LOGGER "INFO -- $NAMENODE jobtracker process running normal"
          LOOP="NO"
       fi
    done
  }
############################
#CHECK SECONDARYNAMENODE PROCESS
############################
function checksecondarynamenode()
  {
    LOOP="YES"
    STARTSNNCOUNT=1

    $PING -c 2 $SECONDARYNAMENODE > /dev/null 2>&1
    if [ $? -ne 0 ]; then
       $LOGGER "ERROR -- can't ping to secondarynamenode $SECONDARYNAMENODE"
       return 200
    fi

    while [ "$LOOP" == "YES" ]
    do
       if [ "X$($SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$SECONDARYNAMENODE "$JDK/bin/jps" | $AWK '{print $2}' | grep -i secondarynamenode)" == "X" ]; then
          $LOGGER "ERROR -- $SECONDARYNAMENODE secondarynamenode process does not start,restart it in $STARTSNNCOUNT times."
          $SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$SECONDARYNAMENODE "$HADOOP/bin/hadoop-daemon.sh start secondarynamenode" > /dev/null 2>&1
          let STARTSNNCOUNT=STARTSNNCOUNT+1
          if [ "$STARTSNNCOUNT" -eq "$STARTCOUNT" ]; then
             $LOGGER "ERROR -- $SECONDARYNAMENODE secondarynamenode be to start $STARTSNNCOUNT times,but it still does not start"
             LOOP="NO"
          fi
          sleep $STARTSLEEPTIME
       else
          $LOGGER "INFO -- $SECONDARYNAMENODE secondarynamenode process running normal"
          LOOP="NO"
       fi
    done
  }
############################
#CHECK DATANODE PROCESS
############################
function checkdatanode()
  {
    DATANODE=$1
    LOOP="YES"
    STARTSNNCOUNT=1

    $PING -c 2 $DATANODE > /dev/null 2>&1
    if [ $? -ne 0 ]; then
       $LOGGER "ERROR -- can't ping to datanode $DATANODE"
       return 201
    fi

    while [ "$LOOP" == "YES" ]
    do
       if [ "X$($SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$DATANODE "$JDK/bin/jps" | $AWK '{print $2}' | grep -i datanode)" == "X" ]; then
          $LOGGER "ERROR -- $DATANODE datanode process does not start,restart it in $STARTSNNCOUNT times."
          $SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$DATANODE "$HADOOP/bin/hadoop-daemon.sh start datanode" > /dev/null 2>&1
          let STARTSNNCOUNT=STARTSNNCOUNT+1
          if [ "$STARTSNNCOUNT" -eq "$STARTCOUNT" ]; then
             $LOGGER "ERROR -- $DATANODE datanode be to start $STARTSNNCOUNT times,but it still does not start"
             LOOP="NO"
          fi
          sleep $STARTSLEEPTIME
       else
          $LOGGER "INFO -- $DATANODE datanode process running normal"
          LOOP="NO"
       fi
    done
  }
############################
#CHECK TASKTRACKER PROCESS
############################
function checktasktracker()
  {
    DATANODE=$1
    LOOP="YES"
    STARTSNNCOUNT=1

    $PING -c 2 $DATANODE > /dev/null 2>&1
    if [ $? -ne 0 ]; then
       $LOGGER "ERROR -- can't ping to datanode $DATANODE"
       return 201
    fi

    while [ "$LOOP" == "YES" ]
    do
       if [ "X$($SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$DATANODE "$JDK/bin/jps" | $AWK '{print $2}' | grep -i tasktracker)" == "X" ]; then
          $LOGGER "ERROR -- $DATANODE tasktracker process does not start,restart it in $STARTSNNCOUNT times."
          $SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$DATANODE "$HADOOP/bin/hadoop-daemon.sh start tasktracker" > /dev/null 2>&1
          let STARTSNNCOUNT=STARTSNNCOUNT+1
          if [ "$STARTSNNCOUNT" -eq "$STARTCOUNT" ]; then
             $LOGGER "ERROR -- $DATANODE tasktracker be to start $STARTSNNCOUNT times,but it still does not start"
             LOOP="NO"
          fi
          sleep $STARTSLEEPTIME
       else
          $LOGGER "INFO -- $DATANODE tasktracker process running normal"
          LOOP="NO"
       fi
    done
  }
############################
#MAIN
############################
MAINLOOP="YES"
while [ "$MAINLOOP" == "YES" ]
 do
   checknamenode
   checkjobtracker
   checksecondarynamenode

   i=1
   while read datanode
    do
       ARRAY_DATANODES[i]=$datanode
       let i=i+1
    done < $HADOOP/conf/slaves

   DATANODESTR=${ARRAY_DATANODES[@]}

   for NODEHOSTNAME in $DATANODESTR
    do
    checkdatanode $NODEHOSTNAME
    checktasktracker $NODEHOSTNAME
    done

    sleep $CHECKSLEEPTIME
 done
############################
exit 0
