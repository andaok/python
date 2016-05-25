#!/bin/bash

scriptroot=$(cd $(dirname $0); pwd)
source $scriptroot/config
rootdir=/Data

cid=$1

mysql -u $user -D $database -h $host --password=$password -e "select unit_code from t_device where index_code='$cid'"
if [ $? != 0 ]; then
    exit 301
fi

x=$(mysql -u $user -D $database -h $host --password=$password -e "select unit_code,router_addr,router_port from t_device where index_code='$cid'"  | sed '1d')
oid=$(echo $x | awk '{print $1}')
ipaddr=$(echo $x | awk '{ print $2 }')
port=$(echo $x | awk '{ print $3 }')
url=$(mysql -u $user -D $database -h $host --password=$password -e "select caiji_addr from t_device where index_code='$cid'" | sed "1d;s#ipaddr#$ipaddr#;s#port#$port#")

x=$(redis-cli -h $rip -p $rport get ${cid}_live)

echo "$oid,$ipaddr,$port" > /tmp/wye.log

echo $x >> /tmp/debug.txt

for i in $(echo $x| sed 's/"//g;s/^.//;s/..$//;s/},/ /g'); do
    n=$(echo $i | awk -F:{ '{print $1}')
    v=$(echo $i | awk -F:{ '{print $2}' | sed 's#,#\n#g') 
    S[$n]=$v
done


x=2
dir=$rootdir/$oid/$cid
log=$dir/live.log
errorlog=$dir/error.log
timestamp=$dir/timestamp
path=$dir/live.m3u8

. /etc/rc.d/init.d/functions
while true; do

    ct=$(date +%H%M%S)
    ct=$(date +%H)
    cw=$(date +%u)
    if [ ! -z $(echo "${S[$cw]}" | grep $ct) ]; then
        echo "$(date +'%F %T') - Current time is $ct, ffmpeg start" >> $log
        while true; do
            wdate=$(date +%Y%m%d)
            wdir=$dir/media/$wdate
            if [ ! -d $wdir ]; then
                mkdir -p $wdir
            fi

            pr=$(ps -ef | grep ffmpeg | grep $cid | grep -v grep | awk '{print $2}')
            if [ ! -z "$pr" ]; then
                kill -9 $pr
            fi

            num=$(echo $((($(date +%s)-$(date -d "$(date +%F)" +%s))/10+1)))
            name="$(date +%Y%m%d)"
            cmd="/usr/local/bin/ffmpeg -d -f rtsp -rtsp_transport tcp -i '$url' -vcodec copy -acodec libfaac -b:a 15k -map 0 -f segment -segment_time 10 -segment_list_size 2 -segment_list_entry_prefix media/$wdate/ -segment_list $path -segment_start_number $num -segment_list_type m3u8 -segment_format mpegts $wdir/$name%05d.ts > /dev/null &"
            daemon $cmd
            
            sleep 10
            if [ ! -f $path ]; then
                echo "$(date +'%F %T') - m3u8 not found, wait" >> $errorlog
            else
                stat $path | awk -F"[.: /-]" '/Modify/{print $3$4$5$6$7$8}' > $timestamp
            fi
            
            while true; do

                echo "--------------------------------------------------------------" >> $log
                ct=$(date +%H%M%S)
                if [ $ct -gt "235900" ]; then
                    x=0
                fi
                if [ $ct -ge "000000" -a $ct -lt "235900" -a $x -eq 0 ]; then
                    echo "$(date +'%F %T') - plan to restart ffmpeg" >> $log
                    echo "$(date +'%F %T') - x value is $x" >> $log
                    x=1
                    continue 2
                fi

                ct=$(date +%H)
                cw=$(date +%u)
                if [ ! -z $(echo "${S[$cw]}" | grep $ct) ]; then
                    echo "$(date +'%F %T') - Current Time is still in working hours, keep working" >> $log
                else
                    echo "$(date +'%F %T') - Current Time is not in working hours, kill ffmpeg and waiting" >> $log
                    kill -9 $(ps -ef | grep ffmpeg | grep $cid | grep -v grep | awk '{print $2}')
                    rm -f $path
                    continue 3
                fi

                sleep 30
                current=$(stat $path | awk -F"[.: /-]" '/Modify/{print $3$4$5$6$7$8}')
                echo "$(date +'%F %T') - current timestamp is $current" >> $log
                oldst=$(cat $timestamp)
                echo "$(date +'%F %T') - the old timestamp is $oldst" >> $log
                if [ -z "$current" ]; then
                    echo "$(date +'%F %T') - m3u8 still not found, please check" >> $errorlog
                    continue 2
                fi
                
                if [ $current -gt $oldst ]; then
                    echo "$(date +'%F %T') - timestamp normally" >> $log
                    echo $current > $timestamp
                else
                    echo "$(date +'%F %T') - timestamp error, try to restart" >> $log
                    continue 2
                fi
            done
        done
    else
        echo "$(date +'%F %T') - Current time is $ct, pass" >> $log
        sleep 30
    fi
done &
mysql -u $user -D $database -h $host --password=$password -e "update t_device set status=1 where index_code='$cid'"
if [ $? != 0 ]; then
    exit 302
fi
