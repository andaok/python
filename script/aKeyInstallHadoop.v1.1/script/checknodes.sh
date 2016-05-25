#!/bin/bash
##########################################################
# Purpose:
#        this script check the nodes that 
#+       from nodes.conf whether meets the following requirements
# Requirements:
#       (1) nodes can be connected
#       (2) if the node is namenode that must install expect
#       (3) this script of hadoop install program must be 
#+          run in namenode 
#       (4) involved directory in the installation process  
#+          must be not exist on each node
# 
# Write by wye in 20120604
# Copyright@2012 Cloudiya Technology
#     
##########################################################
#GET PUBLIC VARIABLES
source $ABSDIR/conf/publicvars.conf
source $ABSDIR/conf/nodes.conf

$ECHO "$DATE -- INFO -- Start check whether meets hadoop install conditions in each node"
#####################################
#COPY SSH-COPY-ID FILE TO /USR/BIN
if [ -e /usr/bin/ssh-copy-id ]; then
   $RM -f /usr/bin/ssh-copy-id
   $CP $ABSDIR/conf/ssh-copy-id /usr/bin/ssh-copy-id
else
   echo "$DATE -- ERROR -- this system does not exist ssh-copy-id file"
   exit 1
fi
#####################################
#CHECK NODES FORMAT
#####################################
#CHECK NAMENODE
ARRAY_NAMENODE=( $NAMENODE )
NAMENODE_NUM=${#ARRAY_NAMENODE[*]}

if [ "$NAMENODE_NUM" -eq "1" ]; then
   echo "$DATE -- INFO -- Namenode is $NAMENODE"
else
   echo "$DATE -- ERROR -- namenode setup error,please again setup it in nodes.conf"
   exit 1
fi
##########################
#CHECK SECONDARYNAMENODE
ARRAY_SECONDARYNAMENODE=( $SECONDARYNAMENODE )
SECONDARYNAMENODE_NUM=${#ARRAY_SECONDARYNAMENODE[*]}
if [ "$SECONDARYNAMENODE_NUM" -eq "1" ]; then
   echo "$DATE -- INFO -- Secondarynamenode is $SECONDARYNAMENODE"
else
   echo "$DATE -- ERROR -- secondarynamenode setup error,please again setup it in nodes.conf"
   exit 1
fi
##########################
#CHECK  DATANODES
ARRAY_DATANODES=( $DATANODES )
DATANODE_NUM=${#ARRAY_DATANODES[*]}

if [ "$DATANODE_NUM" -le "0" ]; then
   echo "$DATE -- ERROR -- the datanode number must be at least two,please setup it in nodes.conf"
   exit 1
else
   echo "$DATE -- INFO -- There are $DATANODE_NUM datanode,namely $DATANODES"
fi
#####################################
#CHECK NAMENODE WHETHER IS LOCALHOST
#####################################
function getipaddress()
 {
   nicnames="eth0 em1"
   for nicname in $nicnames
     do
        $IFCONFIG $nicname > /dev/null 2>&1
        if [ $? -eq 0 ]; then
           NICIPADDRESS=$($IFCONFIG $nicname | $GREP inet | $GREP -v 127.0.0.1 | $GREP -v inet6 | $AWK '{print $2}'| $TR -d  "addr:")
        fi
     done
   echo $NICIPADDRESS
 }

LOCALIPADDRESS=$(getipaddress)

#LOCALIPADDRESS=$($IFCONFIG em1 | $GREP inet | $GREP -v 127.0.0.1 | $GREP -v inet6 | $AWK '{print $2}'| $TR -d  "addr:")

if [ "$LOCALIPADDRESS" != "$NAMENODE" ]; then
   echo "$DATE -- ERROR -- Hadoop install program must be run in namenode,namely $NAMENODE"
   exit 1
fi
#####################################
#CHECK NAMENODE WHETHER IS SECONDARYNAMENODE 
#####################################
if [ "$SECONDARYNAMENODE" == "$NAMENODE" ]; then
   echo "$DATE -- ERROR -- Namenode and Secondarynamenode can not be the same host"
   exit 1
fi
#####################################
#CHECK NAMENODE WHETHER IS DATANODES ONE OF THEM
#####################################
for (( i=0;i<$DATANODE_NUM;i++ ))
do
  if [ "$NAMENODE" == "${ARRAY_DATANODES[i]}" ]; then
     echo "$DATE -- ERROR -- Namenode can't be datanodes one of them"
     exit
  fi
done
####################################
#CHECK SECONDARYNAMENODE WHETHER IS DATANODES ONE OF THEM
####################################
for (( i=0;i<$DATANODE_NUM;i++ ))
do
  if [ "$SECONDARYNAMENODE" == "${ARRAY_DATANODES[i]}" ]; then
     $ECHO -en "Secondarynamenode $SECONDARYNAMENODE and Datanode ${ARRAY_DATANODES[i]} is the same host,if you want to continue with the install,\nPlease enter 'yes',or 'no':"
     read line
     case $line in
     yes|y|YES|Yes|Y) $ECHO "$DATE -- INFO -- Continue hadoop install...";;
        no|n|NO|No|N) exit 1 ;;
                   *) $ECHO "$DATE -- ERROR -- plase input valid string ";exit 1 ;;
     esac
  fi
done
#####################################
#CHECK CONNECTIVITY
#####################################
#CHECK PING TO NAMENODE
$PING -c 2 $NAMENODE > /dev/null 2>&1

if [ $? -eq 0 ]; then
   echo "$DATE -- INFO -- Namenode $NAMENODE can be connected"
else
   echo "$DATE -- ERROR -- Namenode $NAMENODE can't be connected"
   exit 1
fi 
########################
#CHECK PING TO SECONDARYNAMENODE
$PING -c 2 $SECONDARYNAMENODE > /dev/null 2>&1

if [ $? -eq 0 ]; then
   echo "$DATE -- INFO -- Secondarynamenode $SECONDARYNAMENODE can be connected"
else
   echo "$DATE -- ERROR -- Secondarynamenode $SECONDARYNAMENODE can't be connected"
   exit 1
fi
########################
#CHECK PING TO DATANODES

for (( i=0;i<$DATANODE_NUM;i++ ))
do
  $PING -c 2 ${ARRAY_DATANODES[i]} > /dev/null 2>&1
  if [ $? -eq 0 ]; then
     echo "$DATE -- INFO -- Datanode ${ARRAY_DATANODES[i]} can be connected"
  else 
     echo "$DATE -- ERROR -- Datanode ${ARRAY_DATANODES[i]} can't be connected"
     exit 1
  fi
done
#####################################
#CHECK NAMENODE WHETHER INSTALL EXPECT
#####################################
$RPM -qa | $GREP expect > /dev/null 2>&1
if [ $? -ne 0 ]; then
   echo "$DATE -- INFO -- expect is not install,now install..."
   $RPM -i --quiet $ABSDIR/software/tcl-8.5.7-6.el6.x86_64.rpm
   $RPM -i --quiet $ABSDIR/software/expect-5.44.1.15-2.el6.x86_64.rpm
   if [ $? -ne 0 ]; then
      echo "ERROR -- expect install fail"
      exit 1
   fi
fi
#####################################
#CHECK RELATED DIRECTORY WHETHER ALREADY EXIST
#####################################
for (( i=0;i<$DATANODE_NUM;i++ ))
do
 DATANODE="$DATANODE ${ARRAY_DATANODES[i]} "
done

#CHECK HADOOP INSTALL DIRECTORY 
$ECHO "$DATE -- INFO -- Start check hadoop install directory $HADOOPINSTALLDIR" 
CMD="$LS -al $HADOOPINSTALLDIR"
for NODE in $DATANODE $NAMENODE $SECONDARYNAMENODE
do
   $EXPECT -c "set timeout -1;
               spawn $SSH root@$NODE $CMD;
               expect {
                       *assword:* {send -- $HADOOPNODEROOTPWD\r;
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
          0) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- $NODE Directory of $HADOOPINSTALLDIR already exist \033[39;49;0m";exit 1;;
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $NODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $NODE \033[39;49;0m";exit 1;;
        100) $ECHO -e "\033[32;49;1m  $DATE -- INFO -- $NODE Directory of $HADOOPINSTALLDIR does not exist,check pass  \033[39;49;0m";; 
   esac
done

#CHECK HADOOP DATA STORE DIRECTORY
$ECHO "$DATE -- INFO -- Start check hadoop data store directory $HADOOPDATASTOREDIR"
CMD="$LS -al $HADOOPDATASTOREDIR"
for NODE in $DATANODE $NAMENODE $SECONDARYNAMENODE
do
   $EXPECT -c "set timeout -1;
               spawn $SSH root@$NODE $CMD;
               expect {
                       *assword:* {send -- $HADOOPNODEROOTPWD\r;
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
          0) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- $NODE Directory of $HADOOPDATASTOREDIR already exist \033[39;49;0m";exit 1;;
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $NODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $NODE \033[39;49;0m";exit 1;;
        100) $ECHO -e "\033[32;49;1m  $DATE -- INFO -- $NODE Directory of $HADOOPDATASTOREDIR does not exist,check pass  \033[39;49;0m";;
   esac
done
######################################
#CHECK HADOOP USER WHETHER ALREADY EXIST
######################################
$ECHO "$DATE -- INFO -- Start check hadoop user of $HADOOPUSERNAME whether already exist in each node"
CMD="$LESS $PASSWDFILE | $GREP -w $HADOOPUSERNAME"
for NODE in $DATANODE $NAMENODE $SECONDARYNAMENODE
do
   $EXPECT -c "set timeout -1;
               spawn $SSH root@$NODE $CMD;
               expect {
                       *assword:* {send -- $HADOOPNODEROOTPWD\r;
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
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $NODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $NODE \033[39;49;0m";exit 1;;
        103) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Hadoop user of $HADOOPUSERNAME already exist in $NODE,please setup other's hadoop user name in publicvars.conf. \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO -- Hadoop user of $HADOOPUSERNAME is not exist in $NODE,check pass.  \033[39;49;0m";;
   esac
done
######################################
$ECHO "$DATE -- INFO -- all nodes to meet the installation conditions"
exit 0





