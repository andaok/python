#!/bin/bash
####################################################
# Purpose:
#       this script create hadoop environment
#+      for namenode 
#+      
# Description:
#       this script do three things
#+      (1) create "hadoop-user" user and setup password
#+      (2) add sudo permissions to hadoop-user 
#+      (3) create hadoop install directory
#+      (4) copy hadoop binary file to hadoop install directory
#+      (5) copy jdk binary file to jdk install directory
#+      (5) create hadoop data store enviroment       
#+      (6) generate public key in namenode side 
#
# Write by wye in 20120525
# Copyright@2012 cloudiya technology
####################################################
#GET PUBLIC VARIABLES
source $ABSDIR/conf/publicvars.conf
source $ABSDIR/conf/nodes.conf

$ECHO "$DATE -- INFO -- Start initialization namenode......."
##################################
#CREATE HADOOP-USER
$USERADD $HADOOPUSERNAME
if [ $? -ne 0 ]; then
   echo "$DATE -- ERROR -- create hadoop-user fail!"
   exit 1
fi
##################################
#SETUP PASSWORD FOR HADOOP-USER 
$ECHO $HADOOPUSERINITPWD | $PASSWD --stdin $HADOOPUSERNAME
if [ $? -ne 0 ]; then
   echo "$DATE -- ERROR -- setup hadoop-user password fail!"
   exit 1
fi 
##################################
#ADD HADOOP-USER TO SUDOERS FILE
$CHMOD 640 $SUDOERSFILE
if [ $? -ne 0 ]; then
   echo "$DATE -- ERROR -- alter $SUDOERSFILE read and write permissions to 640 fail!"
   exit 1
fi 
$ECHO "$HADOOPUSERNAME ALL=(ALL) NOPASSWD:ALL" >> $SUDOERSFILE
if [ $? -ne 0 ]; then
   echo "$DATE -- ERROR -- add hadoop-user info to $SUDOERSFILE fail!"
   exit 1
fi
$CHMOD 440 $SUDOERSFILE
if [ $? -ne 0 ]; then
   echo "$DATE -- ERROR -- recover $SUDOERSFILE read and write permissions to 440 fail!"
   exit 1
fi
###################################
#CREATE HADOOP INSTALL DIRECTORY
if [ -d $HADOOPINSTALLDIR ]; then
   echo "$DATE -- ERROR -- $HADOOPINSTALLDIR is already exist"
   exit 1
else
   $MKDIR -p $HADOOPINSTALLDIR
   $CHOWN -R $HADOOPUSERNAME:$HADOOPUSERNAME $HADOOPINSTALLDIR
fi
###################################
#COPY HADOOP INSTALL BINARY TO HADOOP INSTALL DIRECTORY
$SUDO -u $HADOOPUSERNAME $TAR -zxf $ABSDIR/software/$HADOOPBINARYFILE -C $HADOOPINSTALLDIR/

if [ "$($LS $HADOOPINSTALLDIR)" != "hadoop" ]; then
   $SUDO -u $HADOOPUSERNAME $MV $HADOOPINSTALLDIR/$($LS $HADOOPINSTALLDIR) $HADOOPINSTALLDIR/hadoop
fi

#COPY JDK BINARY FILE TO JDK INSTALL DIRECTORY
$SUDO -u $HADOOPUSERNAME $TAR -zxf $ABSDIR/software/$JDKBINARYFILE -C $HADOOPINSTALLDIR/

if [ "$($LS $HADOOPINSTALLDIR | $GREP -v hadoop)" != "jdk" ]; then
   $SUDO -u $HADOOPUSERNAME $MV $HADOOPINSTALLDIR/$($LS $HADOOPINSTALLDIR | $GREP -v hadoop)  $HADOOPINSTALLDIR/jdk
fi

###################################
#CREATE HADOOP DATA STORE DIRECTORY
if [ -d $HADOOPDATASTOREDIR ]; then
   echo "$DATE -- ERROR -- $HADOOPDATASTOREDIR is already exist"
   exit 1
else
   $MKDIR -p $HADOOPDATASTOREDIR
   $CHOWN -R $HADOOPUSERNAME:$HADOOPUSERNAME $HADOOPDATASTOREDIR
fi
##################################
#GENERATE PUBLIC KEY FOR NAMENODE SIDE
$SUDO -u $HADOOPUSERNAME $SSHKEYGEN -t rsa -f /home/$HADOOPUSERNAME/.ssh/id_rsa -P "" > /dev/null 2>&1
if [ $? -ne 0 ]; then
   echo "$DATE -- ERROR -- generate public key in namenode fail"
   exit 1
fi
##################################
$ECHO "$DATE -- INFO -- Initialization namenode success!"
exit 0




