#!/bin/bash
####################################################
# Purpose:
#       this script scan each nodes,view related 
#+      process whether or not to start successfully
#
# Attention:
#       this script can be run separately.
#
# Write by wye in 20120528
# Copyright@2012 cloudiya technology
####################################################
RELDIR=`dirname $0`
ABSDIR=`cd $RELDIR;pwd`

################################################
#GET GLOBAL PUBLIC VARIABLES
source $ABSDIR/conf/publicvars.conf
source $ABSDIR/conf/nodes.conf

################################################
$ECHO "$DATE -- INFO -- Start scan each node,please wait......"
#CHECK HADOOP STATUS
#############################
#CHECK NAMENODE STATUS
NODESUC="NO"
TIMECOUNT=0
 
while [ "$NODESUC" == "NO" ]
do
 
if [ "X$($SUDO -u $HADOOPUSERNAME $HADOOPINSTALLDIR/jdk/bin/jps | $AWK '{print $2}' | grep -i namenode)" != "X" -a  "X$($SUDO -u $HADOOPUSERNAME $HADOOPINSTALLDIR/jdk/bin/jps | $AWK '{print $2}' | grep -i jobtracker)" != "X" ]; then
     echo "$DATE -- INFO -- namenode and jobtracker start success"
     NODESUC="YES"
else
     sleep 2
     let TIMECOUNT=TIMECOUNT+2
     if [ "$TIMECOUNT" -ge "10" ]; then
        echo "$DATE -- ERROR -- namenode or jobtracker start fail"
        exit 1
     fi
fi

done
##############################
#CHECK SNN STATUS
NODESUC="NO"
TIMECOUNT=0

while [ "$NODESUC" == "NO" ]
do
  if [ "X$($SUDO -u $HADOOPUSERNAME $SSHNOT $HADOOPUSERNAME@$SECONDARYNAMENODE "$HADOOPINSTALLDIR/jdk/bin/jps" | $AWK '{print $2}' | grep -i secondarynamenode)" != "X" ]; then
     echo "$DATE -- INFO -- secondarynamenode start success"
     NODESUC="YES"
  else
     sleep 2
     let TIMECOUNT=TIMECOUNT+2
     if [ "$TIMECOUNT" -ge "10" ]; then
        echo "$DATE --  ERROR -- secondarynamenode start fail"
        exit 1
     fi
  fi
done
#############################
#CHECK DATANODE STATUS
ARRAY_DATANODES=( $DATANODES )
DATANODE_NUM=${#ARRAY_DATANODES[*]}
#DATANODE=${ARRAY_DATANODES[@]#$SECONDARYNAMENODE}
DATANODE=${ARRAY_DATANODES[@]}

for NODEHOSTNAME in $DATANODE
do
   NODESUC="NO"
   TIMECOUNT=0
  
   while [ "$NODESUC" == "NO" ]
     do
       if [ "X$($SUDO -u $HADOOPUSERNAME $SSHNOT $HADOOPUSERNAME@$NODEHOSTNAME "$HADOOPINSTALLDIR/jdk/bin/jps" | $AWK '{print $2}' | grep -i datanode)" != "X" -a  "X$($SUDO -u $HADOOPUSERNAME $SSHNOT $HADOOPUSERNAME@$NODEHOSTNAME  "$HADOOPINSTALLDIR/jdk/bin/jps" | $AWK '{print $2}' | grep -i tasktracker)" != "X" ]; then
          echo "$DATE -- INFO -- datanode and tasktracker start success in $NODEHOSTNAME"
          NODESUC="YES"
       else
       sleep 2
       let TIMECOUNT=TIMECOUNT+2
        if [ "$TIMECOUNT" -ge "10" ]; then
           echo "$DATE -- ERROR -- datanode or tasktracker start fail in $NODEHOSTNAME"
           exit 1
        fi
      fi
    done
done
###################################################
exit 0

