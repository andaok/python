#!/bin/bash
######################################################################
# Purpose:
#       this script is main program for hadoop cluster install
#
# Write by wye in 20120528
# Copyright@2012 cloudiya technology 
######################################################################
RELDIR=`dirname $0`
ABSDIR=`cd $RELDIR;pwd`

export ABSDIR
################################################
#GET GLOBAL PUBLIC VARIABLES
source $ABSDIR/conf/publicvars.conf
source $ABSDIR/conf/nodes.conf
################################################
#EACH FUNCTIONAL MODULE IS CALLED

$SH $ABSDIR/script/checknodes.sh

if [ $? -eq 0 ]; then
   $SH $ABSDIR/script/initnamenode.sh
else
   exit 1
fi

if [ $? -eq 0 ]; then
   $SH $ABSDIR/script/initsnndatanode.sh
else
   exit 1
fi

if [ $? -eq 0 ]; then
   $SH $ABSDIR/script/inithadoopconf.sh
else
   exit 1
fi

if [ $? -eq 0 ]; then
   $SH $ABSDIR/script/preinteraction.sh
else
   exit 1
fi
###################################################
#FORMAT NAMENODE
$SUDO -u $HADOOPUSERNAME $HADOOPINSTALLDIR/hadoop/bin/hadoop namenode -format

if [ $? -ne 0 ]; then
   echo "$DATE -- ERROR -- format namenode fail"
   exit 1
fi

#START HADOOP
$SUDO -u $HADOOPUSERNAME $HADOOPINSTALLDIR/hadoop/bin/start-all.sh

if [ $? -ne 0 ]; then
   echo "$DATE -- ERROR -- start hadoop fail"
   exit 1
fi
###################################################
#SCAN EACH NODES TO VIEW RELATED PROCESS WHETHER START
if [ $? -eq 0 ]; then
   $SH $ABSDIR/scannodes.sh
else
   exit 1
fi
##################################################
if [ $? -eq 0 ]; then
   $SH $ABSDIR/script/finishnamenode.sh
else
   exit 1
fi
#################################################
$ECHO "$DATE -- INFO -- Install hadoop success!"
exit 0














