#!/bin/bash
#######################################################
# Purpose:
#    this script have three function 
#    (1) install hadoopclient 
#    (2) install fusehadoopclient 
#    (3) mount hdfs to local directory
# Usage:
#    ./Install.sh hadoopclient
#    ./Install.sh fuseclient
#    ./Install.sh mounthdfs namenodeaddress mountdirectory
# Version 1.0:
#    hadoop 1.0.1
#    jdk 1.7.0.3
# 
# Write by wye in 20120602
# Copyright@2012 cloudiya technology
########################################################
RELDIR=`dirname $0`
ABSDIR=`cd $RELDIR;pwd`
#############################
#GLOBAL VARIABLES
InstallPackagePath=$ABSDIR
InstallDefaultPath="/opt/cloudiyaDataMount"
NAMENODEPORT="50081"
#############################
#SYSTEM COMMAND
CP=/bin/cp
MKDIR=/bin/mkdir
WHICH=/usr/bin/which
LN=/bin/ln
RPM=/bin/rpm
YUM=/usr/bin/yum
PING=/bin/ping
LS=/bin/ls
CAT=/bin/cat
MOUNT=/bin/mount
GREP=/bin/grep
NOHUP=/usr/bin/nohup
SED=/bin/sed
ECHO=/bin/echo
#############################
#HADOOPCLIENT INSTALL
#############################
function hadoopClientInstall()
 { 
   echo "Start hadoop client install,please wait...."
   if [ ! -d $InstallDefaultPath ]; then
      $MKDIR -p $InstallDefaultPath
   else
      echo " hadoopclient insatll directory \"$InstallDefaultPath\" already exist"
      exit 1      
   fi
   
   #COPY HADOOP BINARY PACKAGE TO INSTALLPATH
   $CP -r $InstallPackagePath/HADOOP $InstallDefaultPath

   #COPY JDK BINARY PACKAGE TO INSTALLPATH
   $CP -r $InstallPackagePath/JDK $InstallDefaultPath

   {
    echo ""
    echo "export HADOOP_HOME=$InstallDefaultPath/HADOOP"
    echo "export JAVA_HOME=$InstallDefaultPath/JDK"
    echo ""
   } >> $InstallDefaultPath/HADOOP/conf/hadoop-env.sh

   echo "hadoopclient install to $InstallDefaultPath/HADOOP/"
   echo "hadoopclient install success!"
  
 }
#############################
#FUSECLIENT INSTALL
#############################
function fuseClientInstall()
 {
   echo "Start fuse client install,please wait...."

   $WHICH  fuse_dfs_wrapper.sh  > /dev/null 2>&1

   if [ $? -eq 0 ]; then
      echo "fuse_dfs_wrapper.sh is already exist"
      exit 1
   fi
   
   if [ ! -d $InstallDefaultPath ]; then
      $MKDIR -p $InstallDefaultPath
   else
      echo " fuseclient insatll directory \"$InstallDefaultPath\" already exist"
      exit 1
   fi

   #COPY HADOOP BINARY PACKAGE TO INSTALLPATH
   $CP -r $InstallPackagePath/HADOOP $InstallDefaultPath

   #COPY JDK BINARY PACKAGE TO INSTALLPATH
   $CP -r $InstallPackagePath/JDK $InstallDefaultPath
   
   {
    echo ""
    echo "export HADOOP_HOME=$InstallDefaultPath/HADOOP"
    echo "export JAVA_HOME=$InstallDefaultPath/JDK"
    echo ""
   } >> $InstallDefaultPath/HADOOP/conf/hadoop-env.sh

   
   #FUSE-DFS DEPENDS ON THE FUSE,FUSE-LIBS,CHECK FUSE,FUSE-LIBS
   $RPM -ivh --test $InstallPackagePath/SOFTWARE/fuse-libs-2.8.3-4.el6.x86_64.rpm
   if [ $? -eq 0 ]; then
      $YUM -y install $InstallPackagePath/SOFTWARE/fuse-libs-2.8.3-4.el6.x86_64.rpm  > /dev/null 2>&1 
   fi

   $RPM -ivh --test $InstallPackagePath/SOFTWARE/fuse-2.8.3-4.el6.x86_64.rpm
   if [ $? -eq 0 ]; then
      $YUM -y install $InstallPackagePath/SOFTWARE/fuse-2.8.3-4.el6.x86_64.rpm  > /dev/null 2>&1
   fi

   #ALERT fuse_dfs_wrapper.sh
   
   $CAT /dev/null > $InstallDefaultPath/HADOOP/build/contrib/fuse-dfs/fuse_dfs_wrapper.sh   

   HADOOP_HOME=$InstallDefaultPath/HADOOP
   JAVA_HOME=$InstallDefaultPath/JDK
   
   {
      echo "#--------------fuse-dfs env variables--------------#"
      echo "export HADOOP_HOME=$InstallDefaultPath/HADOOP"
      echo "export JAVA_HOME=$InstallDefaultPath/JDK"
      echo "for f in ls $HADOOP_HOME/lib/*.jar $HADOOP_HOME/*.jar ; do"
      echo "export  CLASSPATH="'$CLASSPATH:$f'
      echo "done"
      echo "export OS_ARCH=amd64"
      echo "export LD_LIBRARY_PATH=$JAVA_HOME/jre/lib/amd64/server:$JAVA_HOME/jre/lib/amd64:$HADOOP_HOME/build/c++/Linux-amd64-64/lib:/usr/local/lib:/usr/lib"
      echo "$InstallDefaultPath/HADOOP/build/contrib/fuse-dfs/fuse_dfs -obig_writes "'$@'
   } >> $InstallDefaultPath/HADOOP/build/contrib/fuse-dfs/fuse_dfs_wrapper.sh

   $LN -s $InstallDefaultPath/HADOOP/build/contrib/fuse-dfs/fuse_dfs_wrapper.sh /usr/local/bin/fuse_dfs_wrapper.sh
   $LN -s $InstallDefaultPath/HADOOP/build/contrib/fuse-dfs/fuse_dfs /usr/local/bin/fuse_dfs
   
   echo "fuseclient install to $InstallDefaultPath/HADOOP/"
   echo "fuseclient install success!"

 }
###############################
#MOUNT LOCAL DIRECTORY TO HDFS
###############################
function mounthdfs() 
 {
   NAMENODEADDRESS=$1
   TMPMOUNTDIRECTORY=$2
   MOUNTDIRECTORY=`$ECHO $TMPMOUNTDIRECTORY | $SED 's/\/$//g'`
   
   
   if [ ! -d $InstallDefaultPath/HADOOP/build/contrib/fuse-dfs ]; then
      echo "No fusehadoopclient in $InstallDefaultPath,"
      exit 1
   fi

   $PING -c 2 $NAMENODEADDRESS > /dev/null 2>&1

   if [ $? -ne 0 ]; then
      echo "Namenode \"$NAMENODEADDRESS\" can't be connected,please check."
      exit 1
   fi   
   
   if [ ! -d $MOUNTDIRECTORY ]; then
      echo "Mount directory \"$MOUNTDIRECTORY\" does not exist."
      exit 1
   fi

   $MOUNT | $GREP fuse | $GREP $MOUNTDIRECTORY > /dev/null 2>&1

   if [ $? -eq 0 ]; then
      echo "Directory $MOUNTDIRECTORY already has been mounted,Can no longer be mounted"
      exit 1
   fi

   $InstallDefaultPath/HADOOP/build/contrib/fuse-dfs/fuse_dfs_wrapper.sh  dfs://$NAMENODEADDRESS:$NAMENODEPORT/  $MOUNTDIRECTORY -o nonempty > mounthdfs.log 2>&1

   sleep 10   

   $LS $MOUNTDIRECTORY > /dev/null 2>&1

   if [ $? -eq 0 ]; then
      $MOUNT | $GREP fuse | $GREP $MOUNTDIRECTORY > /dev/null 2>&1
      if [ $? -eq 0 ]; then
         echo "mount hdfs to local directory \"$MOUNTDIRECTORY\" success!"
      else
         echo "mount hdfs to local directory \"$MOUNTDIRECTORY\" fail!"
         exit 1
      fi
   else
      echo "mount hdfs to local directory \"$MOUNTDIRECTORY\" fail!"
      exit 1
   fi 

   $CP $ABSDIR/checkFuseProcess.sh $InstallDefaultPath

   $NOHUP $InstallDefaultPath/checkFuseProcess.sh  $NAMENODEADDRESS  $MOUNTDIRECTORY > /dev/null 2>&1 &

   echo -e "Would you like to mount the directory automatically at system startup?"
   read line
   case $line in
        yes|y|YES|Yes|Y)
        echo "$NOHUP $InstallDefaultPath/checkFuseProcess.sh  $NAMENODEADDRESS  $MOUNTDIRECTORY > /dev/null 2>&1 &" >> /etc/rc.d/rc.local 
        echo "Add mount command to /etc/rc.d/rc.local";;
        no|n|NO|No|N) exit 1 ;;
                   *) echo "plase input valid string ";exit 1 ;;
   esac
      
 }
############################
function usage()
 {
  echo "Usage:"
  echo "./Install.sh hadoopclient"
  echo "./Install.sh fuseclient"
  echo "./Install.sh mounthdfs namenodeaddress mountdirectory"
 }
#############################
#MAIN
#############################
case $1 in
     hadoopclient)
     if [ "$#" == "1" ]; then
        hadoopClientInstall
     else
        echo "Usage : \"./Install.sh hadoopclient\""
        exit 1
     fi
     ;;
     fuseclient)
     if [ "$#" == "1" ]; then
        fuseClientInstall
     else
        echo "Usage : \"./Install.sh fuseclient\""
        exit 1
     fi
     ;;
     mounthdfs)
     if [ "$#" == "3" ]; then
        NAMENODEADDRESS=$2
        MOUNTDIRECTORY=$3
        mounthdfs $NAMENODEADDRESS  $MOUNTDIRECTORY
     else
        echo "Usage : \"./Install.sh mounthdfs namenodeaddress localmountdirectory\""
        exit 1
     fi
     ;;
     "")
     echo "please setup arguments for install.sh"
     usage
     exit 1
     ;;
     *)
     echo "arguments setup error for install.sh"
     usage
     exit 1
     ;;
esac
###############################
exit 0
 

    
    
    



 
      
    
