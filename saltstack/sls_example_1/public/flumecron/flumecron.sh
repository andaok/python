#/bin/bash
. /etc/init.d/functions
source /etc/profile
java -jar /web/flume/log/log-statistic/ServerLogStatistic.jar source-log-info /web/flume/log/log-statistic/logfilepath.properties kafka92:9092,kafka93:9092,kafka94:9092 -1
