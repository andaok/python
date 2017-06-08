#!/bin/bash
#############################################
# Purpose:
#    Execute update in upstream host,Main Include:
#   (1) stop tomcat 
#   (2) backup old war package (optional)
#   (3) delete old war package,copy new war package to webapps dir
#   (4) start tomcat
#   (5) check whether the tomcat startup is successful
#
# Author : weiye
# Date   : 20160817
##################################################

JAVA_HOME="/usr/java/jdk1.7.0_79/"
PATH=$JAVA_HOME/bin:$PATH
CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar

export JAVA_HOME
export CLASSPATH
export PATH

WorkSpace_Dir="/home/weiye/jenkins/"
Tomcat_Dir="/usr/tomcat/"

#STOP TOMCAT
${Tomcat_Dir}/bin/shutdown.sh

#DELETE OLD APPLICATION
rm -rf ${Tomcat_Dir}/webapps/ROOT{,.war}

#COPY NEW WAR PACKAGE TO WEBAPPS
cp $WorkSpace_Dir/ROOT.war  ${Tomcat_Dir}/webapps/

#RESTART TOMCAT
/usr/bin/nohup ${Tomcat_Dir}/bin/startup.sh  > /dev/null 2>&1 &
 
#OPTIONAL
#CHECK WHETHER THE TOMCAT STARTUP SUCCESS

