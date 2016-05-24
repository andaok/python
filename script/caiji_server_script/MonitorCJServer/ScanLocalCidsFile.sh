#!/bin/bash
# --------------------------------------------- /
# Purpose:
#       Scan Local server cids file for get running
#+      on the local server's camera cid
# @author : wye
# @date: 2014-09-10
# @achieve basic functions
# ---------------------------------------------- /

CidsInLocalFile=$1
CidsStr=""

if [ ! -s $CidsInLocalFile ];then
   echo "$CidsInLocalFile not exist or content is null" >&2
   exit 404
fi

while read cid
do 
   CidsStr=${cid}","${CidsStr}
done < $CidsInLocalFile

CidsStr=`echo $CidsStr | sed "s/,$//"`
echo $CidsStr 

exit 0
