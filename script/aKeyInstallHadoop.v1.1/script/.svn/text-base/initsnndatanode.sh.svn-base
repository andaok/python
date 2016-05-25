#!/bin/bash
####################################################
# Purpose:
#       this script create hadoop environment for 
#+      secondarynamenode and datanode 
#+      
# Description:
#       this script do three things
#+      (1) create "hadoop-user" user and setup password
#+      (2) create hadoop install directory
#+      (3) create hadoop data store directory       
#+         
# Write by wye in 20120525
# Copyright@2012 cloudiya technology
####################################################
#GET PUBLIC VARIABLES
source $ABSDIR/conf/publicvars.conf
source $ABSDIR/conf/nodes.conf

#GET DATANODES INFOMATION
ARRAY_DATANODES=( $DATANODES )
DATANODE_NUM=${#ARRAY_DATANODES[*]}

#for (( i=0;i<$DATANODE_NUM;i++ ))
#do
# DATANODE="$DATANODE ${ARRAY_DATANODES[i]} "
#done

DATANODE=${ARRAY_DATANODES[@]#$SECONDARYNAMENODE}

echo "$DATANODE $SECONDARYNAMENODE"

$ECHO "$DATE -- INFO -- Start initalization secondarynamenode and datanode............."
##################################
#CREATE HADOOP-USER
$ECHO "$DATE -- INFO -- Start create run the hadoop's user in snn and datanodes,namely $HADOOPUSERNAME"
CMD="$USERADD $HADOOPUSERNAME"
for NODE in $DATANODE $SECONDARYNAMENODE
do
   $EXPECT -c "set timeout -1;
               spawn $SSHNOT root@$NODE $CMD;
               expect {
                       *assword:* {send -- $HADOOPNODEROOTPWD\r;
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
        100) $ECHO -en "\033[32;49;1m  hadoop user of $HADOOPUSERNAME already exist or $HADOOPUSERNAME home directory of /home/$HADOOPUSERNAME already exist in $NODE,\nyou wang to continue install,please enter 'yes',or'no' \033[39;49;0m"
             read line
             case $line in
                  yes|y|YES|Yes|Y) $ECHO "$DATE -- INFO -- Continue hadoop install...";;
                     no|n|NO|No|N) exit 1 ;;
                                *) $ECHO "$DATE -- ERROR -- plase input valid string ";exit 1 ;;
             esac
             ;;
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $NODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $NODE \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO -- hadoop user of $HADOOPUSERNAME create success in $NODE  \033[39;49;0m";;
   esac
done


$ECHO "$DATE -- INFO -- Start setup hadoop user of $HADOOPUSERNAME home directory to $HADOOPUSERNAME:$HADOOPUSERNAME"
CMD="$CHOWN -R $HADOOPUSERNAME:$HADOOPUSERNAME /home/$HADOOPUSERNAME"

for NODE in $DATANODE $SECONDARYNAMENODE
do
   $EXPECT -c "set timeout -1;
               spawn $SSH root@$NODE $CMD;
               expect {
                       *assword:* {send -- $HADOOPNODEROOTPWD\r;
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
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $NODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $NODE \033[39;49;0m";exit 1;;
        103) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Hadoop user of $HADOOPUSERNAME is not exist in $NODE \033[39;49;0m";exit 1;;
        104) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Hadoop user home directory of /home/$HADOOPUSERNAME is not exist in $NODE \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO --  Setup /home/$HADOOPUSERNAME privileges to $HADOOPUSERNAME:$HADOOPUSERNAME success in $NODE  \033[39;49;0m";;
   esac
   done
##################################
#SETUP PASSWORD FOR HADOOP-USER 
$ECHO "$DATE -- INFO -- Start setup password for $HADOOPUSERNAME in snn and datanodes"
CMD="$ECHO $HADOOPUSERINITPWD | $PASSWD --stdin $HADOOPUSERNAME"

for NODE in $DATANODE $SECONDARYNAMENODE
do
   $EXPECT -c "set timeout -1;
               spawn $SSH root@$NODE $CMD;
               expect {
                       *assword:* {send -- $HADOOPNODEROOTPWD\r;
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
        100) $ECHO -e "\033[32;49;1m  $DATE -- INFO --hadoop user of $HADOOPUSERNAME setup password success in $NODE  \033[39;49;0m";;
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $NODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $NODE \033[39;49;0m";exit 1;;
        103) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- hadoop user of $HADOOPUSERNAME is not exist in $NODE  \033[39;49;0m";exit 1;;
   esac
done

###################################
#CREATE HADOOP INSTALL DIRECTORY
$ECHO "$DATE -- INFO -- Start create hadoop install directory in snn and datanodes"
CMD="$MKDIR -p $HADOOPINSTALLDIR"

for NODE in $DATANODE $SECONDARYNAMENODE
do
   $EXPECT -c "set timeout -1;
               spawn $SSH root@$NODE $CMD;
               expect {
                       *assword:* {send -- $HADOOPNODEROOTPWD\r;
                                    expect {
                                            *denied* {exit 101;}
                                             eof
                                           }
                                  }
                       eof  {exit 102;}
                      }
              "

   case $? in
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $NODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $NODE \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO -- Create hadoop install directory of $HADOOPINSTALLDIR success in $NODE  \033[39;49;0m";;
   esac
done

$ECHO "$DATE -- INFO -- Start setup $HADOOPINSTALLDIR to $HADOOPUSERNAME:$HADOOPUSERNAME"
CMD="$CHOWN -R $HADOOPUSERNAME:$HADOOPUSERNAME $HADOOPINSTALLDIR"

for NODE in $DATANODE $SECONDARYNAMENODE
do
   $EXPECT -c "set timeout -1;
               spawn $SSH root@$NODE $CMD;
               expect {
                       *assword:* {send -- $HADOOPNODEROOTPWD\r;
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
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $NODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $NODE \033[39;49;0m";exit 1;;
        103) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Hadoop user of $HADOOPUSERNAME is not exist in $NODE \033[39;49;0m";exit 1;;
        104) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Hadoop install directory of $HADOOPINSTALLDIR is not exist in $NODE \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO --  Setup $HADOOPINSTALLDIR privileges to $HADOOPUSERNAME:$HADOOPUSERNAME success in $NODE  \033[39;49;0m";;
   esac
done


###################################
#CREATE HADOOP DATA STORE DIRECTORY
$ECHO "$DATE -- INFO -- Start create hadoop data store directory in snn and datanodes"
CMD="$MKDIR -p $HADOOPDATASTOREDIR"

for NODE in $DATANODE $SECONDARYNAMENODE
do
   $EXPECT -c "set timeout -1;
               spawn $SSH root@$NODE $CMD;
               expect {
                       *assword:* {send -- $HADOOPNODEROOTPWD\r;
                                    expect {
                                            *denied* {exit 101;}
                                             eof
                                           }
                                  }
                       eof  {exit 102;}
                      }
              "

   case $? in
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $NODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $NODE \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO -- Create hadoop install directory of $HADOOPDATASTOREDIR success in $NODE  \033[39;49;0m";;
   esac
done

$ECHO "$DATE -- INFO -- Start setup $HADOOPDATASTOREDIR to $HADOOPUSERNAME:$HADOOPUSERNAME"
CMD="$CHOWN -R $HADOOPUSERNAME:$HADOOPUSERNAME $HADOOPDATASTOREDIR"

for NODE in $DATANODE $SECONDARYNAMENODE
do
   $EXPECT -c "set timeout -1;
               spawn $SSH root@$NODE $CMD;
               expect {
                       *assword:* {send -- $HADOOPNODEROOTPWD\r;
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
        101) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Root password error to $NODE \033[39;49;0m";exit 1;;
        102) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Connection refused or time out to $NODE \033[39;49;0m";exit 1;;
        103) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Hadoop user of $HADOOPUSERNAME is not exist in $NODE \033[39;49;0m";exit 1;;
        104) $ECHO -e "\033[32;49;1m  $DATE -- ERROR -- Hadoop install directory of $HADOOPDATASTOREDIR is not exist in $NODE \033[39;49;0m";exit 1;;
          0) $ECHO -e "\033[32;49;1m  $DATE -- INFO --  Setup $HADOOPDATASTOREDIR privileges to $HADOOPUSERNAME:$HADOOPUSERNAME success in $NODE  \033[39;49;0m";;
   esac
done


##################################
$ECHO "$DATE -- INFO -- Intialization secondarynamenode and datanode success !"
exit 0




