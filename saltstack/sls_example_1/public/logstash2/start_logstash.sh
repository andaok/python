#!/bin/bash
PS=`ps -ef | grep logstash-hadoop|grep -v grep |awk '{print $2}'`
/bin/kill -9 $PS


/web/logstash/logstash-1.4.2/bin/logstash agent -f /web/logstash/logstash-hadoop.conf &
