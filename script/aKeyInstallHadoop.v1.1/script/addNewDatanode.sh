#!/bin/bash
#############################################
# Purpose:
#       add new datanode for running hadooop cluster
# 
# Write by wye
# Copyright@2012 cloudiya technology 
#############################################
##CONFFILEPATHFLAG##
#source addNewDatanode.conf
############################
#SYSTEM COMMAND
USERADD=/usr/sbin/useradd
PASSWD=/usr/bin/passwd
ECHO=/bin/echo
CHMOD=/bin/chmod
SUDO=/usr/bin/sudo
MKDIR=/bin/mkdir
TAR=/bin/tar
LS=/bin/ls
RM=/bin/rm
CHOWN=/bin/chown
SSHKEYGEN=/usr/bin/ssh-keygen
SH=/bin/sh
SED=/bin/sed
MV=/bin/mv
GREP=/bin/grep
CP=/bin/cp
PYTHON=/usr/bin/python
RPM=/bin/rpm
EXPECT=/usr/bin/expect
SSHCOPYID=/usr/bin/ssh-copy-id
SSH="/usr/bin/ssh -t -o stricthostkeychecking=no"
SSHNOT="/usr/bin/ssh -o stricthostkeychecking=no"
SCP=/usr/bin/scp
AWK=/bin/awk
CAT=/bin/cat
PING=/bin/ping
IFCONFIG=/sbin/ifconfig
TR=/usr/bin/tr
LESS=/usr/bin/less
NOHUP=/usr/bin/nohup
RCLOCAL=/etc/rc.d/rc.local
############################
#SYSTEM DIRECTORY
PASSWDFILE=/etc/passwd
###########################
#STATIC VARIBALES
DATE=$(date +%Y%m%d-%H:%M:%S)
HADOOPUSERINITPWD="cloudiyaprivatecloud"
############################
#MAIN
############################
#CHECK INSTALL ENVIROMENT
$SUDO -u $HADOOPUSERNAME $HADOOPINSTALLDIR/jdk/bin/jps | $AWK '{print $2}' | grep -i namenode > /dev/null 2>&1
if [ $? -ne 0 ]; then
   $ECHO "$DATE -- ERROR -- Add new datanode script must be run in namenode host!"
   exit 1
fi
############################
#GET NEW DATANODE IPADDRESS
$ECHO -en "please input new datanode ipaddress or hostname:"
read line
$PING -c 2 $line > /dev/null 2>&1
if [ $? -eq 0 ]; then
   DATANODE=$line
else
   echo -e "\033[32;49;1m  $DATE -- ERROR -- Can't ping to $line,please setup correct ipaddress or hostname for new datanode. \033[39;49;0m"
   exit 1   
fi
#GET NEW DATANODE HOST ROOT PASSWORD 
$ECHO -en "please input new datanode host's root password:"
read line
CMD="$LS -al /var"
$EXPECT -c "set timeout -1;
               spawn $SSH root@$DATANODE $CMD;
               expect {
                       *assword:* {send -- $line\r;
                                    expect {
                                            *denied* {exit 101;}
                                            *cannot* {exit 100;}
                                             eof
                                           }
                                  }
                       eof  {exit 102;}
                      }
              "  

   case $? in
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $DATANODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $DATANODE \033[39;49;0m";exit 1;;
          0) DATANODEROOTPWD=$line;;
   esac
###########################
#CHECK RELATED INFOMATION WHETHER ALREADY EXIST IN NEW DATANODE
function checkdir() 
  {
    NODE=$1
    DIR=$2
    CMD="$LS -al $DIR"
    $EXPECT -c "set timeout -1;
               spawn $SSH root@$NODE $CMD;
               expect {
                       *assword:* {send -- $DATANODEROOTPWD\r;
                                    expect {
                                            *denied* {exit 101;}
                                            *cannot* {exit 100;}
                                             eof
                                           }
                                  }
                       eof  {exit 102;}
                      }
              "  
   case $? in
          0) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- $NODE Directory of $DIR already exist \033[39;49;0m";exit 1;;
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $NODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $NODE \033[39;49;0m";exit 1;;
        100) $ECHO -e "\033[32;49;1m  $DATE -- INFO -- $NODE Directory of $DIR does not exist,check pass  \033[39;49;0m";;
   esac 
  }

#CHECK HADOOP INSTALL DIRECTORY IN NEW DATANODE
checkdir $DATANODE $HADOOPINSTALLDIR
#CHECK HADOOP DATA STORE DIRECTORY IN NEW DATANODE
checkdir $DATANODE $HADOOPDATASTOREDIR

#CHECK HADOOP USER WHETHER ALREADY EXIST
CMD="$LESS $PASSWDFILE | $GREP -w $HADOOPUSERNAME"
$EXPECT -c "set timeout -1;
               spawn $SSH root@$DATANODE $CMD;
               expect {
                        *assword:* {send -- $DATANODEROOTPWD\r;
                                    expect {
                                            *denied* {exit 101;}
                                            *$HADOOPUSERNAME* {exit 103;}
                                             eof
                                           }
                                  }
                       eof  {exit 102;}
                      }
              "

   case $? in
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $DATANODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $DATANODE \033[39;49;0m";exit 1;;
        103) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Hadoop user of $HADOOPUSERNAME already exist in $DATANODE,please setup other's hadoop user name in publicvars.conf. \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO -- Hadoop user of $HADOOPUSERNAME is not exist in $DATANODE,check pass.  \033[39;49;0m";;
   esac
##########################
#CREATE HADOOP-USER
CMD="$USERADD $HADOOPUSERNAME"
$EXPECT -c "set timeout -1;
               spawn $SSHNOT root@$DATANODE $CMD;
               expect {
                       *assword:* {send -- $DATANODEROOTPWD\r;
                                    expect {
                                            *denied* {exit 101;}
                                            *exists* {exit 100;}
                                             eof
                                           }
                                  }
                       eof  {exit 102;}
                      }
              "

   case $? in
        100) $ECHO -en "\033[32;49;1m  hadoop user of $HADOOPUSERNAME already exist or $HADOOPUSERNAME home directory of /home/$HADOOPUSERNAME already exist in $DATANODE,\nyou wang to continue install,please enter 'yes',or'no' \033[39;49;0m"
             read line
             case $line in
                  yes|y|YES|Yes|Y) $ECHO "$DATE -- INFO -- Continue hadoop install...";;
                     no|n|NO|No|N) exit 1 ;;
                                *) $ECHO "$DATE -- ERROR -- plase input valid string ";exit 1 ;;
             esac
             ;;
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $DATANODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $DATANODE \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO -- hadoop user of $HADOOPUSERNAME create success in $DATANODE  \033[39;49;0m";;
   esac
#########################
#SETUP PASSWORD FOR HADOOP-USER
CMD="$ECHO $HADOOPUSERINITPWD | $PASSWD --stdin $HADOOPUSERNAME"
$EXPECT -c "set timeout -1;
               spawn $SSH root@$DATANODE $CMD;
               expect {
                       *assword:* {send -- $DATANODEROOTPWD\r;
                                    expect {
                                            *denied* {exit 101;}
                                            *successfully* {exit 100;}
                                            *nknown* {exit 103;}
                                             eof
                                           }
                                  }
                       eof  {exit 102;}
                      }
              "

   case $? in
        100) $ECHO -e "\033[32;49;1m  $DATE -- INFO --hadoop user of $HADOOPUSERNAME setup password success in $DATANODE  \033[39;49;0m";;
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $DATANODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $DATANODE \033[39;49;0m";exit 1;;
        103) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- hadoop user of $HADOOPUSERNAME is not exist in $DATANODE  \033[39;49;0m";exit 1;;
   esac
#########################
#CREATE HADOOP INSTALL DIRECTORY
CMD="$MKDIR -p $HADOOPINSTALLDIR"
$EXPECT -c "set timeout -1;
               spawn $SSH root@$DATANODE $CMD;
               expect {
                       *assword:* {send -- $DATANODEROOTPWD\r;
                                    expect {
                                            *denied* {exit 101;}
                                             eof
                                           }
                                  }
                       eof  {exit 102;}
                      }
              "

   case $? in
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $DATANODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $DATANODE \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO -- Create hadoop install directory of $HADOOPINSTALLDIR success in $DATANODE  \033[39;49;0m";;
   esac

CMD="$CHOWN -R $HADOOPUSERNAME:$HADOOPUSERNAME $HADOOPINSTALLDIR"
$EXPECT -c "set timeout -1;
               spawn $SSH root@$DATANODE $CMD;
               expect {
                       *assword:* {send -- $DATANODEROOTPWD\r;
                                    expect {
                                            *denied* {exit 101;}
                                            *invalid* {exit 103;}
                                            *cannot* {exit 104;}
                                             eof
                                           }
                                  }
                       eof  {exit 102;}
                      }
              "

   case $? in
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $DATANODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $DATANODE \033[39;49;0m";exit 1;;
        103) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Hadoop user of $HADOOPUSERNAME is not exist in $DATANODE \033[39;49;0m";exit 1;;
        104) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Hadoop install directory of $HADOOPINSTALLDIR is not exist in $DATANODE \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO --  Setup $HADOOPINSTALLDIR privileges to $HADOOPUSERNAME:$HADOOPUSERNAME success in $DATANODE  \033[39;49;0m";;
   esac
#########################
#CREATE HADOOP DATA STORE DIRECTORY
CMD="$MKDIR -p $HADOOPDATASTOREDIR"
$EXPECT -c "set timeout -1;
               spawn $SSH root@$DATANODE $CMD;
               expect {
                       *assword:* {send -- $DATANODEROOTPWD\r;
                                    expect {
                                            *denied* {exit 101;}
                                             eof
                                           }
                                  }
                       eof  {exit 102;}
                      }
              "

   case $? in
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $DATANODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $DATANODE \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO -- Create hadoop install directory of $HADOOPDATASTOREDIR success in $DATANODE  \033[39;49;0m";;
   esac

CMD="$CHOWN -R $HADOOPUSERNAME:$HADOOPUSERNAME $HADOOPDATASTOREDIR"
$EXPECT -c "set timeout -1;
               spawn $SSH root@$DATANODE $CMD;
               expect {
                       *assword:* {send -- $DATANODEROOTPWD\r;
                                    expect {
                                            *denied* {exit 101;}
                                            *invalid* {exit 103;}
                                            *cannot* {exit 104;}
                                             eof
                                           }
                                  }
                       eof  {exit 102;}
                      }
              "

   case $? in
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $DATANODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $DATANODE \033[39;49;0m";exit 1;;
        103) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Hadoop user of $HADOOPUSERNAME is not exist in $DATANODE \033[39;49;0m";exit 1;;
        104) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Hadoop install directory of $HADOOPDATASTOREDIR is not exist in $DATANODE \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO --  Setup $HADOOPDATASTOREDIR privileges to $HADOOPUSERNAME:$HADOOPUSERNAME success in $DATANODE  \033[39;49;0m";;
   esac
#########################
#COPY NAMENODE PUBLIC KEY TO NEW DATANODE
$EXPECT -c "set timeout 30;
           spawn $SUDO -u $HADOOPUSERNAME $SSHCOPYID $HADOOPUSERNAME@$DATANODE;
           expect {
                   *password:* {
                                send -- $HADOOPUSERINITPWD\r;
                                expect {
                                        *denied* {exit 101;}
                                         eof
                                       }
                               }
                               eof  {exit 101;}
                  }
          "

if [ $? -eq 101 ]; then
   $ECHO -e "\033[32;49;1m $DATE -- ERROR -- copy hadoop namenode public key to $DATANODE fail \033[39;49;0m"
   exit 1
fi

#CHECK NO PASSWORD LOGIN TO NODE
$SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$DATANODE > /dev/null 2>&1  <<EOF
exit
EOF

if [ $? -ne 0 ]; then
   $ECHO -e "\033[32;49;1m $DATE -- ERROR -- check no password login to $DATANODE fail \033[39;49;0m"
   exit 1
fi

$ECHO "$DATE -- INFO -- Start copy data to new datanode,please wait......"
##########################
#COPY HADOOP BINARY FILE AND JDK BINARY FILE TO NEW DATANODE
$SUDO -u $HADOOPUSERNAME $SCP -r $HADOOPINSTALLDIR/*  $HADOOPUSERNAME@$DATANODE:$HADOOPINSTALLDIR/  > /dev/null 2>&1  
##########################
#START ADD NEW DATANODE ACTION
##########################
#ADD NEW DATANODE IPADDRESS TO INCLUDE FILE
$SUDO -u $HADOOPUSERNAME $ECHO $DATANODE  >> $HADOOPINSTALLDIR/hadoop/conf/include
##########################
#REFRESH DATANODES
$SUDO -u $HADOOPUSERNAME $HADOOPINSTALLDIR/hadoop/bin/hadoop dfsadmin -refreshNodes > /dev/null 2>&1
##########################
#ADD NEW DATANODE IPADDRESS TO SLAVES FILE
$SUDO -u $HADOOPUSERNAME $ECHO $DATANODE >> $HADOOPINSTALLDIR/hadoop/conf/slaves
##########################
#START NEW DATANODE
$SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$DATANODE  "$HADOOPINSTALLDIR/hadoop/bin/hadoop-daemon.sh start datanode" > /dev/null 2>&1
#START NEW TASKTRACKER
$SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$DATANODE  "$HADOOPINSTALLDIR/hadoop/bin/hadoop-daemon.sh start tasktracker" > /dev/null 2>&1
##########################
LOOP="YES"
TIMECOUNT=0

while [ "$LOOP" == "YES" ]
  do
    if [ "X$($SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$DATANODE "$HADOOPINSTALLDIR/jdk/bin/jps" | $AWK '{print $2}' | grep -i datanode)" == "X" ]; then
       sleep 5
       let TIMECOUNT=TIMECOUNT+5
       if [ "$TIMECOUNT" -ge "30" ]; then
          echo "$DATE -- ERROR -- datanode process start fail!"
          exit 1
       fi
    else
       echo "$DATE -- INFO -- datanode process start success!"
       LOOP="NO"
    fi
  done

LOOP="YES"
TIMECOUNT=0

while [ "$LOOP" == "YES" ]
  do
    if [ "X$($SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$DATANODE "$HADOOPINSTALLDIR/jdk/bin/jps" | $AWK '{print $2}' | grep -i tasktracker)" == "X" ]; then
       sleep 5
       let TIMECOUNT=TIMECOUNT+5
       if [ "$TIMECOUNT" -ge "30" ]; then
          echo "$DATE -- ERROR -- tasktracker process start fail!"
          exit 1
       fi
    else
       echo "$DATE -- INFO -- tasktracker process start success!"
       LOOP="NO"
    fi
  done
##########################
$ECHO "$DATE -- INFO -- Add new datanode success!"
$ECHO "$DATE -- INFO -- Start balancer......"
$SUDO -u $HADOOPUSERNAME $HADOOPINSTALLDIR/hadoop/bin/start-balancer.sh -threshold 5
##########################
exit 0


