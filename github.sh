#!/bin/bash

#############################
#THIS SCRIPT FOR EASY TO MANAGE GITHUB
#############################

PROJECTDIR="/var/data/github/python"
GITHUBREPO="andaok/python.git"

#SWITCH TO PROJECT DIR
cd $PROJECTDIR

CMD=$1
COMMIT=$2
DATE=$(date "+%Y%m%d/%H%M")

if [ "X$CMD" == "Xadd" ]; then
{
   echo "START ADD AND UPDATE DATA TO GITHUB IN $DATE"
   echo "-----------------------"
   git add $PROJECTDIR 
   git commit -m "$COMMIT" $PROJECTDIR 
   git push -u origin master
   echo "-----------------------"
} >> /tmp/github.log 2>&1
fi

if [ "X$CMD" == "Xupdate" ]; then
{
   echo "START UPDATE DATA TO GITHUB IN $DATE"
   echo "-----------------------"
   git commit -m "$COMMIT" $PROJECTDIR
   git push -u origin master
   echo "-----------------------"
} >> /tmp/github.log 2>&1
fi

#############################
exit 0

