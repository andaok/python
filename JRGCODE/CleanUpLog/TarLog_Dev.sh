#!/bin/bash

function HandleLog()
{
 cd /usr/tomcat/bin/logs

 date1=`date +%Y%m%d -d '1 days ago'`
 date2=`date +%F -d '1 days ago'`
 deldate=`date +%Y%m%d -d '30 days ago'`

 tar zcvf activity.${date1}.tar.gz  activity.${date2}.*.log  && rm -f activity.${date2}.*.log

 rm -f activity.${deldate}.tar.gz
}

function TmpHandleLog()
{
 year=2017
 month=02

 cd /usr/tomcat/bin/logs

 days=( 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 )
 daysnum=${#days[*]}

 for((i=0;i<daysnum;i++))
 do
 day=${days[i]}
 tar zcvf activity.${year}${month}${day}.tar.gz activity.${year}-${month}-${day}.*.log  && rm -f activity.${year}-${month}-${day}.*.log
 done 
}

HandleLog
