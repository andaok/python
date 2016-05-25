#!/bin/bash
###############################
RELDIR=`dirname $0`
ABSDIR=`cd $RELDIR;pwd`

PYTHON="/usr/bin/python"
ECHO="/bin/echo"
CURL="/usr/bin/curl"
###############################

ARGNUM=$#

###############################
function step1() 
  {
    if [ $? -eq 0 ]; then
       $PYTHON $ABSDIR/CheckAndInit.py
    else
       exit 1
    fi 
  }

function step2()
  {
    if [ $? -eq 0 ]; then
       $PYTHON $ABSDIR/HandleEndlist.py
    else
       exit 1
    fi
  }

function step3()
  {
    if [ $? -eq 0 ]; then
       $PYTHON $ABSDIR/HandleVidSet.py
    else
       exit 1
    fi
  }

function step4()
  {
    if [ $? -eq 0 ]; then
       $PYTHON $ABSDIR/HandleUidSet.py
    else
       exit 1
    fi
  }

function step5()
  {
    if [ $? -eq 0 ]; then
       $PYTHON $ABSDIR/WriteData.py
    else
       exit 1
    fi
  }


function step6()
  {
    if [ $? -eq 0 ]; then
       $PYTHON $ABSDIR/WritePlaylist.py
    else
       exit 1
    fi
  }


function step7()
  {
    if [ $? -eq 0 ]; then
       echo "call php interface : " >> /tmp/BatchPro.log
       $CURL "http://www.skygrande.com/tasks/pack"  >> /tmp/BatchPro.log 2>&1       
    else
       exit 1
    fi
  }


###############################

case $ARGNUM in
        0) STARTSTEP=1
           ;;
        1) if [ $1 -le 7 ] 2>/dev/null ;then
              STARTSTEP=$1
           else
              echo "Usage : `basename $0` STARTSTEP(LESS THAN OR EQUAL FIVE)"
              exit 1
           fi
           ;;
        *) echo "Usage : `basename $0` STARTSTEP(LESS THAN OR EQUAL FIVE) "
           exit 1 
           ;;
esac
###############################

DATE=$(date +%Y%m%d-%H:%M:%S)
$ECHO "--------$DATE Handle Start----------"

for ((i=$STARTSTEP;i<=7;i++))
  do
      step${i}
  done

DATE=$(date +%Y%m%d-%H:%M:%S)
$ECHO "--------$DATE Handle End------------"
$ECHO ""
$ECHO ""

###############################

exit 0


