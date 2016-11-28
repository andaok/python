#!/bin/bash
# ----------------------------------------------------

metric=$1
tmp_file=/tmp/tmp_tcp_status.txt
/usr/sbin/ss -t4 state all | awk '{++S[$1]} END {for (a in S) {printf "%11-s %s\n",a,S[a]}}' > $tmp_file

case $metric in
   CLOSED)
          output=$(awk '/CLOSED/{print $2}' $tmp_file)
          if [ "$output" == "" ];then
             echo 0
          else
             echo $output
          fi
        ;;
   LISTEN)
          output=$(awk '/LISTEN/{print $2}' $tmp_file)
          if [ "$output" == "" ];then
             echo 0
          else
             echo $output
          fi
        ;;
   SYN-RECV)
          output=$(awk '/SYN-RECV/{print $2}' $tmp_file)
          if [ "$output" == "" ];then
             echo 0
          else
             echo $output
          fi
        ;;
   SYN-SENT)
          output=$(awk '/SYN-SENT/{print $2}' $tmp_file)
          if [ "$output" == "" ];then
             echo 0
          else
             echo $output
          fi
        ;;
   ESTABLISHED)
          output=$(awk '/ESTAB/{print $2}' $tmp_file)
          if [ "$output" == "" ];then
             echo 0
          else
             echo $output
          fi
        ;;
   TIME-WAIT)
          output=$(awk '/TIME-WAIT/{print $2}' $tmp_file)
          if [ "$output" == "" ];then
             echo 0
          else
             echo $output
          fi
        ;;
   CLOSING)
          output=$(awk '/CLOSING/{print $2}' $tmp_file)
          if [ "$output" == "" ];then
             echo 0
          else
             echo $output
          fi
        ;;
   CLOSE-WAIT)
          output=$(awk '/CLOSE-WAIT/{print $2}' $tmp_file)
          if [ "$output" == "" ];then
             echo 0
          else
             echo $output
          fi
        ;;
   LAST-ACK)
          output=$(awk '/LAST-ACK/{print $2}' $tmp_file)
          if [ "$output" == "" ];then
             echo 0
          else
             echo $output
          fi
         ;;
   FIN-WAIT-1)
          output=$(awk '/FIN-WAIT-1/{print $2}' $tmp_file)
          if [ "$output" == "" ];then
             echo 0
          else
             echo $output
          fi
         ;;
   FIN-WAIT-2)
          output=$(awk '/FIN-WAIT-2/{print $2}' $tmp_file)
          if [ "$output" == "" ];then
             echo 0
          else
             echo $output
          fi
         ;;
         *)
          echo "USAGE : $0 [CLOSED|LISTEN|SYN-RECV|SYN-SENT|ESTABLISHED|TIME-WAIT|CLOSING|CLOSE-WAIT|LAST-ACK|FIN-WAIT-1|FIN-WAIT-2]"   
esac

