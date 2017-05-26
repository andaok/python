#!/bin/bash
IP=`awk '{print $1}' /tmp/mess.txt |sed -n '1p'`
for FILE in `awk '{print $2}' /tmp/mess.txt`
	do
		DIRNAME=`dirname $FILE`
		scp $FILE 223.202.30.62:/home/logstash/hadoop_logdata/$IP/2015/$DIRNAME
	done
