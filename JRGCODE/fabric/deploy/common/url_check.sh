#!/bin/sh

CHECK_URL=$1
#check whether parameter valid, unless remind of USEAGE
if [ $# -ne 1 ];then
  echo "[ERROR]USEAGE:$0 CHECK_URL"
  exit 1
fi

#echo "[INFO]check whether the url is ok"
_RETVAL=0
RETRY_CNT=5
while (( RETRY_CNT > 0 )); do
   if [ "$(echo $CHECK_URL|grep -c ^post)" -eq "1" ];then
      POST_URL=`echo $CHECK_URL|sed 's/^post//'`
    curl -i --head --connect-timeout 15 --max-time 20 -I -X POST  $POST_URL 2>&1 | grep -E 'HTTP.* 200 OK' > /dev/null||curl -i --head --connect-timeout 15 --max-time 20 -I -X POST  $POST_URL 2>&1 | grep -E 'HTTP.* 302 Found' > /dev/null
  else
        curl --connect-timeout 15 --max-time 20 -I -s $CHECK_URL 2>&1 | grep -E 'HTTP.* 200 OK' > /dev/null || curl --connect-timeout 15 --max-time 20 -I -s $CHECK_URL 2>&1 | grep -E 'HTTP.* 302 Found' > /dev/null
  fi
  
  #curl --connect-timeout 20 --max-time 15 -I -s $CHECK_URL 2>&1 | grep -i 'HTTP.* 302 FOUND'  > /dev/null || curl --connect-timeout 20 --max-time 15 -I -s $CHECK_URL 2>&1 | grep -i 'HTTP.* 200 OK' > /dev/null
  if (($?==0));then
    break
  else 
    let RETRY_CNT--
  fi
done
[ $RETRY_CNT -eq 0 ] && _RETVAL=1 || _RETVAL=0
if((_RETVAL==1));then
  echo "[ERROR]Check Application Status Fail"
  exit 1
elif((_RETVAL==0));then
 echo "[INFO]Check Application Status OK"   
fi

