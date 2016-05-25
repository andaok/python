#!/bin/bash
################################################
# Purpose:
#       this script do finishing work for namenode
#
# Description:
#        this script do two things
#        (1) add hadoop enviroment to /etc/profile
#        (2) delete sudoer for hadoop user in /etc/sudoers
#
# Write by wye in 20120608
# Copyright@2012 cloudiya technology
###############################################
#GET PUBLIC VARIABLES
source $ABSDIR/conf/publicvars.conf
source $ABSDIR/conf/nodes.conf

###############################################
#ADD ENVIROMENT TO /ETC/PROFILE FILE

{
 $ECHO ""
 $ECHO ""
 $ECHO "HADOOP_HOME=$HADOOPINSTALLDIR/hadoop"
 $ECHO "JAVA_HOME=$HADOOPINSTALLDIR/jdk"
 $ECHO "export HADOOP_HOME JAVA_HOME"
 $ECHO "export PATH="'$HADOOP_HOME'"/bin:"'$JAVA_HOME'"/bin:"'$JAVA_HOME'"/jre/bin:"'$JAVA_HOME'"/bin:$PATH"
 $ECHO ""
} >> $PROFILE

source $PROFILE
########################################
#@@@@@@@@@@@@@@@@@@@@@@
#START HADOOP PROCESS MONITOR SCRTPT
#@@@@@@@@@@@@@@@@@@@@@@
########################################
$SUDO -u $HADOOPUSERNAME $NOHUP $HADOOPINSTALLDIR/hadoop/bin/checkHadoopProcess.sh > /dev/null 2>&1 & 
########################################
#@@@@@@@@@@@@@@@@@@@@@@
#ALTER HDFS ROOT DIRECTORY PERMISSIONS
#@@@@@@@@@@@@@@@@@@@@@@
########################################
$SUDO -u $HADOOPUSERNAME $HADOOPINSTALLDIR/hadoop/bin/hadoop fs -chown $HDFSROOTDIRCHOWN:$HDFSROOTDIRCHOWN / > /dev/null 2>&1
$SUDO -u $HADOOPUSERNAME $HADOOPINSTALLDIR/hadoop/bin/hadoop fs -chmod $HDFSROOTDIRCHMOD / > /dev/null 2>&1 
########################################
#AFTER IN HADOOP INSTALL,CREATE SOME DIR.
$SUDO -u $HDFSROOTDIRCHOWN $HADOOPINSTALLDIR/hadoop/bin/hadoop fs -mkdir /backup  > /dev/null 2>&1
$SUDO -u $HDFSROOTDIRCHOWN $HADOOPINSTALLDIR/hadoop/bin/hadoop fs -mkdir /cdrom   > /dev/null 2>&1
########################################
exit 0
