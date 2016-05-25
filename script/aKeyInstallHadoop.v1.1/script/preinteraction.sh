#!/bin/bash
###################################################################
# Description:
#         this script copy hadoop related file to other nodes of 
#+        secondarynamenode and datanode
#
# Purpose:
#         this is script do three things
#+        (1) copy namenode public key to datanode or snn nodes
#+        (2) check no password login for each datanode or snn nodes
#+        (3) copy hadoop binary file to each datanode or snn node
#
# Write by wye in 20120529
# Copyright@2012 cloudiya technology
###################################################################
#GET PUBLIC VARIABLES
source $ABSDIR/conf/publicvars.conf
source $ABSDIR/conf/nodes.conf

#################################################
#COPY NAMENODE PUBLIC KEY AND SOFTWARE BINARY FILE TO DATANODES
ARRAY_DATANODES=( $DATANODES )
DATANODE_NUM=${#ARRAY_DATANODES[*]}
DATANODE=${ARRAY_DATANODES[@]#$SECONDARYNAMENODE}

for NODEHOSTNAME in $DATANODE $NAMENODE
do
#COPY NAMENODE PUBLIC KEY TO NODE
$EXPECT -c "set timeout 30;
           spawn $SUDO -u $HADOOPUSERNAME $SSHCOPYID $HADOOPUSERNAME@$NODEHOSTNAME;
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
   $ECHO -e "\033[32;49;1m $DATE -- ERROR -- copy hadoop namenode public key to $NODEHOSTNAME fail \033[39;49;0m"
   exit 1
fi

#CHECK NO PASSWORD LOGIN TO NODE
$SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$NODEHOSTNAME > /dev/null 2>&1  <<EOF
exit
EOF

if [ $? -ne 0 ]; then
   $ECHO -e "\033[32;49;1m $DATE -- ERROR -- check no password login to $NODEHOSTNAME fail \033[39;49;0m"
   exit 1
fi

#COPY HADOOP BINARY FILE AND JDK BINARY FILE TO NODE
$SUDO -u $HADOOPUSERNAME $SCP -r $HADOOPINSTALLDIR/*  $HADOOPUSERNAME@$NODEHOSTNAME:$HADOOPINSTALLDIR/  > /dev/null 2>&1  

done
##################################################
#COPY NAMENODE PUBLIC KEY AND SOFTWARE BINARY FILE TO SNNNODE
while read NODEHOSTNAME
do
#COPY NAMENODE PUBLIC KEY TO NODE
$EXPECT -c "set timeout 30;
           spawn $SUDO -u $HADOOPUSERNAME $SSHCOPYID $HADOOPUSERNAME@$NODEHOSTNAME;
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
   $ECHO -e "\033[32;49;1m $DATE -- ERROR -- copy hadoop namenode public key to $NODEHOSTNAME fail \033[39;49;0m"
   exit 1
fi

#CHECK NO PASSWORD LOGIN TO NODE
$SUDO -u $HADOOPUSERNAME $SSH $HADOOPUSERNAME@$NODEHOSTNAME > /dev/null 2>&1 <<EOF
exit
EOF

if [ $? -ne 0 ]; then
   $ECHO -e "\033[32;49;1m $DATE -- ERROR -- check no password login to $NODEHOSTNAME fail \033[39;49;0m"
   exit 1
fi

#COPY HADOOP BINARY FILE AND JDK BINARY FILE TO NODE
$SUDO -u $HADOOPUSERNAME $SCP -r $HADOOPINSTALLDIR/*  $HADOOPUSERNAME@$NODEHOSTNAME:$HADOOPINSTALLDIR/  > /dev/null 2>&1

done < $HADOOPINSTALLDIR/hadoop/conf/masters
##################################################
exit 0








