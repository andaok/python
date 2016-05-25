#!/bin/bash
####################################################
# Description:
#         this script initialization hadoop configure
# Purpose:
#         this is script do things
#+        (1) alter hadoop configure file,include
#+            core-site.xml,hdfs-site.xml,mapred-site.xml
#+            slaves,masters,include
#+        (2) alter hadoop enviroment file of hadoop-env.conf
#
# Write by wye in 20120529
# Copyright@2012 cloudiya technology
####################################################
#GET PUBLIC VARIABLES
source $ABSDIR/conf/publicvars.conf
source $ABSDIR/conf/nodes.conf
####################################################
STHADOOPINSTALLDIR=$($ECHO $HADOOPINSTALLDIR | $SED 's/\//\\\//g')

$ECHO "$DATE -- INFO -- Start initalization hadoop configure file"
####################################################
#DEAL WITH HADOOP OLD CONFIGURE FILE
function dealwithfile() 
   {
    FILE=$1
    if [ -e $HADOOPINSTALLDIR/hadoop/conf/$FILE ]; then
       $RM -f $HADOOPINSTALLDIR/hadoop/conf/$FILE
       $SUDO -u $HADOOPUSERNAME $CP $ABSDIR/hadoopconf/$FILE $HADOOPINSTALLDIR/hadoop/conf/$FILE
    fi 
   }

dealwithfile core-site.xml
dealwithfile hdfs-site.xml
dealwithfile mapred-site.xml
dealwithfile hadoop-env.sh
dealwithfile masters
dealwithfile slaves
dealwithfile include
dealwithfile hadoop-metrics2.properties
###################################################
#ALTER HADOOP ENVIROMENT FILE OF hadoop-env.sh
$SUDO -u $HADOOPUSERNAME $SED -i '1i\export JAVA_HOME='$HADOOPINSTALLDIR'/jdk' $HADOOPINSTALLDIR/hadoop/conf/hadoop-env.sh
$SUDO -u $HADOOPUSERNAME $SED -i '1i\export HADOOP_HOME='$HADOOPINSTALLDIR'/hadoop' $HADOOPINSTALLDIR/hadoop/conf/hadoop-env.sh
###################################################
#ALTER HADOOP CONFIGURE FILE OF core-site.xml
$SUDO -u $HADOOPUSERNAME $PYTHON $ABSDIR/script/handlexml.py $HADOOPINSTALLDIR/hadoop/conf/core-site.xml fs.default.name hdfs://$NAMENODE:50081
$SUDO -u $HADOOPUSERNAME $PYTHON $ABSDIR/script/handlexml.py $HADOOPINSTALLDIR/hadoop/conf/core-site.xml hadoop.tmp.dir $HADOOPDATASTOREDIR/tmp
$SUDO -u $HADOOPUSERNAME $PYTHON $ABSDIR/script/handlexml.py $HADOOPINSTALLDIR/hadoop/conf/core-site.xml fs.checkpoint.dir $HADOOPDATASTOREDIR/snn
###################################################
#ALTER HADOOP CONFIGURE FILE OF hdfs-site.xml
$SUDO -u $HADOOPUSERNAME $PYTHON $ABSDIR/script/handlexml.py $HADOOPINSTALLDIR/hadoop/conf/hdfs-site.xml dfs.data.dir $HADOOPDATASTOREDIR/dfs/data
$SUDO -u $HADOOPUSERNAME $PYTHON $ABSDIR/script/handlexml.py $HADOOPINSTALLDIR/hadoop/conf/hdfs-site.xml dfs.name.dir $HADOOPDATASTOREDIR/dfs/name
$SUDO -u $HADOOPUSERNAME $PYTHON $ABSDIR/script/handlexml.py $HADOOPINSTALLDIR/hadoop/conf/hdfs-site.xml dfs.http.address $NAMENODE:50071
$SUDO -u $HADOOPUSERNAME $PYTHON $ABSDIR/script/handlexml.py $HADOOPINSTALLDIR/hadoop/conf/hdfs-site.xml dfs.secondary.http.address $SECONDARYNAMENODE:50090
###################################################
#ALTER HADOOP CONFIGURE FILE OF mapred-site.xml
$SUDO -u $HADOOPUSERNAME $PYTHON $ABSDIR/script/handlexml.py $HADOOPINSTALLDIR/hadoop/conf/mapred-site.xml mapred.job.tracker $NAMENODE:50082
###################################################
#ALTER HADOOP CONFIGURE FILE OF masters
$SUDO -u $HADOOPUSERNAME $ECHO $SECONDARYNAMENODE >> $HADOOPINSTALLDIR/hadoop/conf/masters
###################################################
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#ALTER HADOOP CONFIFURE FILE OF hadoop-metrics2.properties
#SPECIFY THE GANGLIA SERVER ADDRESS INSTEAD OF A BROADCAST ADDRESS
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###################################################
{
 $SUDO -u $HADOOPUSERNAME $ECHO "namenode.sink.ganglia.servers=$GANGLIASERVER"
 $SUDO -u $HADOOPUSERNAME $ECHO "datanode.sink.ganglia.servers=$GANGLIASERVER"
 $SUDO -u $HADOOPUSERNAME $ECHO "jobtracker.sink.ganglia.servers=$GANGLIASERVER"
 $SUDO -u $HADOOPUSERNAME $ECHO "tasktracker.sink.ganglia.servers=$GANGLIASERVER"
 $SUDO -u $HADOOPUSERNAME $ECHO "maptask.sink.ganglia.servers=$GANGLIASERVER"
 $SUDO -u $HADOOPUSERNAME $ECHO "reducetask.sink.ganglia.servers=$GANGLIASERVER" 
} >> $HADOOPINSTALLDIR/hadoop/conf/hadoop-metrics2.properties
###################################################
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#HADOOP RELATED PROCESS MONITOR,PROCESS FAULT AUTO RESTART.
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###################################################
#COPY MONITOR SCRIPT TO RELATED DIRECTORY
$SUDO -u $HADOOPUSERNAME $CP $ABSDIR/conf/checkHadoopProcess.conf $HADOOPINSTALLDIR/hadoop/conf/checkHadoopProcess.conf
$SUDO -u $HADOOPUSERNAME $CP $ABSDIR/script/checkHadoopProcess.sh $HADOOPINSTALLDIR/hadoop/bin/checkHadoopProcess.sh

#WRITE RELATED INFOMATION TO CHECKHADOOPPROCESS.CONF
{
$SUDO -u $HADOOPUSERNAME $ECHO "HADOOPINSTALLDIR=$HADOOPINSTALLDIR" 
$SUDO -u $HADOOPUSERNAME $ECHO "HADOOPUSERNAME=$HADOOPUSERNAME" 
$SUDO -u $HADOOPUSERNAME $ECHO "NAMENODE=\"$NAMENODE\"" 
$SUDO -u $HADOOPUSERNAME $ECHO "SECONDARYNAMENODE=\"$SECONDARYNAMENODE\"" 
$SUDO -u $HADOOPUSERNAME $ECHO "DATANODES=\"$DATANODES\""
} >> $HADOOPINSTALLDIR/hadoop/conf/checkHadoopProcess.conf

#WRITE CHECKHADOOPPROCESS.CONF PATH TO CHECKHADOOPPROCESS.SH
$SED -i "s/##CONFFILEPATHFLAG##/&\nsource $STHADOOPINSTALLDIR\/hadoop\/conf\/checkHadoopProcess.conf/"  $HADOOPINSTALLDIR/hadoop/bin/checkHadoopProcess.sh

#HADOOP MONITOR SCRIPT WITH THE SYSTEM BOOT
$ECHO "$SUDO -u $HADOOPUSERNAME $NOHUP $HADOOPINSTALLDIR/hadoop/bin/checkHadoopProcess.sh > /dev/null 2>&1 &" >> $RCLOCAL
###################################################
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#ADD NEW DATANODE PROGRAM
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###################################################
#COPY ADD NEW DATANODE SCRIPT TO RELATED DIRECTORY
$SUDO -u $HADOOPUSERNAME $CP $ABSDIR/conf/addNewDatanode.conf $HADOOPINSTALLDIR/hadoop/conf/addNewDatanode.conf
$SUDO -u $HADOOPUSERNAME $CP $ABSDIR/script/addNewDatanode.sh $HADOOPINSTALLDIR/hadoop/bin/addNewDatanode.sh

#WRITE RELATED INFOMATION TO ADDNEWDATANODE.CONF
{
$SUDO -u $HADOOPUSERNAME $ECHO "HADOOPINSTALLDIR=$HADOOPINSTALLDIR"
$SUDO -u $HADOOPUSERNAME $ECHO "HADOOPDATASTOREDIR=$HADOOPDATASTOREDIR"
$SUDO -u $HADOOPUSERNAME $ECHO "HADOOPUSERNAME=$HADOOPUSERNAME"
$SUDO -u $HADOOPUSERNAME $ECHO "NAMENODE=\"$NAMENODE\""
$SUDO -u $HADOOPUSERNAME $ECHO "SECONDARYNAMENODE=\"$SECONDARYNAMENODE\""
$SUDO -u $HADOOPUSERNAME $ECHO "DATANODES=\"$DATANODES\""
} >> $HADOOPINSTALLDIR/hadoop/conf/addNewDatanode.conf

#WRITE ADDNEWDATANODE.CONF PATH TO ADDNEWDATANODE.SH
$SED -i "s/##CONFFILEPATHFLAG##/&\nsource $STHADOOPINSTALLDIR\/hadoop\/conf\/addNewDatanode.conf/"  $HADOOPINSTALLDIR/hadoop/bin/addNewDatanode.sh
###################################################
ARRAY_DATANODES=( $DATANODES )
DATANODE_NUM=${#ARRAY_DATANODES[*]}

for (( i=0;i<$DATANODE_NUM;i++ ))
do

#ALTER HADOOP CONFIGURE FILE OF slaves
$SUDO -u $HADOOPUSERNAME $ECHO ${ARRAY_DATANODES[i]} >> $HADOOPINSTALLDIR/hadoop/conf/slaves

#ALTER HADOOP CONFIGURE FILE OF include
$SUDO -u $HADOOPUSERNAME $ECHO ${ARRAY_DATANODES[i]} >> $HADOOPINSTALLDIR/hadoop/conf/include

done
#################################################
$ECHO "$DATE -- INFO -- Initalization hadoop configure success"
exit 0





