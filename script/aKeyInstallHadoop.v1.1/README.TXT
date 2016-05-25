
BEFORE INSTALLING,PLEASE READ CAREFULLY THE TEXT BELOW.
###########################################################
 Attention:
     (1) before installing,your need alter conf/nodes.conf file
         and conf/publicvars.conf file for youself install.
         described in detail in these two file,please carefully
         read them.good luck.
     (2) please comment the line "Defaults requiretty" in /etc/sudoers

 Version 1.1 description:
     (1) base on hadoop 1.0.3 and jdk 1.7.0.3
     (2) repair secondarynamenode can not do the checkpoint
     (3) add ganglia monitor support
 Version 1.2 description:
     (1) add hadoop related process monitor,process fault auto restart.
 Version 1.3 description:
     (1) fix ssh related bug,add ssh command option.
 Version 1.4 description
     (1) specify the ganglia server address instead of a broadcast address. 
 Version 1.5 description
     (1) add namenode no password to login to localhost
 Version 1.6 description
     (2) repalce namenode NIC name to em1,Modify HDFS root directory permissions.
 Version 1.7 description
     (1) add script for add new datanode to running hadoop cluster
 Version 2.0
     (1) after in hadoop install , create some dir.
     
        
 Usage: ./install.sh

 Author: yewei  wye@cloudiya.com

 Date: 2012.05.28

 Copyright@2012 cloudiya technology 
###########################################################
