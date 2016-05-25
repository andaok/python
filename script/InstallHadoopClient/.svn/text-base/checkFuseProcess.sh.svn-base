#!/bin/bash
###########################################
# Purpose:
#      check directory whether mount to hdfs success
#+     if no,mount this directory to hdfs
#+     this check script scan one time per $checktime
# Usage:
#      ./checkFuseProcess.sh namenodeaddress mountdirectory
# 
# Write by wye in 20120705
# Copyright@2012 cloudiya technology
###########################################
#SYSTEM COMMAND
PING=/bin/ping
MOUNT=/bin/mount
GREP=/bin/grep
LS=/bin/ls
LOGGER="/usr/bin/logger -i -t hadoopfuse"
############################
#STATIC VARIABLES
InstallDefaultPath="/opt/cloudiyaDataMount"
checktime=900
NAMENODEPORT="50081"
NAMENODE=$1
MNTDIR=$2
############################
#MAIN
############################
if [ ! -d $InstallDefaultPath/HADOOP/build/contrib/fuse-dfs ]; then
   $LOGGER "ERROR -- Can't find hadoopfuseclient install directory,script checkFuseProcess.sh quit"
   exit 1
fi

LOOP="YES"

while [ "$LOOP" == "YES" ]
do

$PING -c 2 $NAMENODE  > /dev/null 2>&1

if [ $? -eq 0 ]; then
   $MOUNT | $GREP fuse | $GREP $MNTDIR > /dev/null 2>&1
   if [ $? -eq 0 ]; then
      $LS $MNTDIR > /dev/null 2>&1
      if [ $? -ne 0 ]; then
         $LOGGER "ERR0R -- May be due to hadoop failure,led to mount $MNTDIR to $NAMENODE fail!,please wait recover"
      fi
   else
      $LOGGER "INFO -- Mount $MNTDIR to $NAMENODE"
      $InstallDefaultPath/HADOOP/build/contrib/fuse-dfs/fuse_dfs_wrapper.sh  dfs://$NAMENODE:$NAMENODEPORT/  $MNTDIR -o nonempty > /dev/null 2>&1 &
   fi         
else
   $LOGGER "ERROR -- Can't ping to namenode $NAMENODE,temporarily mount $MNTDIR to $NAMENODE fail!,please wait recover"   
fi

sleep $checktime
done
############################ 
exit 0
