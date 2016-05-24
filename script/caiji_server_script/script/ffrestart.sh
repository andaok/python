#!/bin/bash

scriptroot=$(cd $(dirname $0); pwd)
cid=$1

kill -9 $(ps -ef | grep ffstart | grep $cid | grep -v grep | awk '{ print $2 }') > /dev/null
kill -9 $(ps -ef | grep ffmpeg | grep $cid | grep -v grep | awk '{ print $2 }') > /dev/null

/usr/bin/python $scriptroot/ffstart.py $cid





