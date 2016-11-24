#!/bin/env bash
###AUTHOR:zhangkai
###DATE:2016.10.14
#VERSION : V1.1

usage()
{
cat << EOF
Usage: $0 OPTIONS
  -?                show help
  --ACTION          start      -start application
                    stop       -stop application
                    restart    -restart application
                    update     -place project package
                    backup     -backup target directory
                    deploy     -do "backup-stop-update-start-url_check"
                    auto       -auto deploy
  --TOMCAT_HOME     directory of application home
  --APP_NAME        application name
  --dir_src         source directory of backup
  --dir_dest        destination directory of bacup
  --dir_update      directory of update
  --CHECK_URL       url
EOF
}

for f in $(find ~/deploy -name '*.sh'); do
  [ -x "$f" ] || chmod u+x "$f"
done

#check whether parameter valid, unless remind of USEAGE
[ $# -eq 0 ] && { usage; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
      --ACTION)
        shift
        ACTION="$1"
        ;;
      --TOMCAT_HOME)
        shift
        TOMCAT_HOME="$1"
        ;;
      --APP_NAME)
        shift
        APP_NAME="$1"
        ;;
      --dir_src)
        shift
        dir_src="$1"
        ;;
      --dir_dest)
        shift
        dir_dest="$1"
        ;;
      --dir_update)
        shift
        dir_update="$1"
        ;;
      --CHECK_URL)
        shift
        CHECK_URL="$1"
        ;;
      *)
        echo "UNKNOWN ARGUMENTS: $1" 1>&2
        usage
        exit 1
        ;;
    esac

    shift
  done

case $ACTION in
start)
    #startup_tomcat
    sh ~/deploy/tomcat/start.sh "$TOMCAT_HOME"  && \
    #url_check
    sh ~/deploy/common/url_check.sh "$CHECK_URL"
    ;;
stop)
   #stop_tomcat
   sh ~/deploy/tomcat/stop.sh "$TOMCAT_HOME" 
    ;;
restart)
    #stop_tomcat
    sh ~/deploy/tomcat/stop.sh "$TOMCAT_HOME"  && \
   # startup_tomcat
   sh ~/deploy/tomcat/start.sh "$TOMCAT_HOME"  && \
   #url_check
    sh ~/deploy/common/url_check.sh "$CHECK_URL"
    ;;
update)
   # update
   sh ~/deploy/tomcat/update.sh "$TOMCAT_HOME" "$APP_NAME" "$dir_update"  
    ;;
backup)
   #backup
   sh ~/deploy/common/backup.sh "$dir_src" "$dir_dest" "$APP_NAME"
   ;;
deploy)
  #backup
   sh ~/deploy/common/backup.sh "$dir_src" "$dir_dest" "$APP_NAME"  && \
  #stop_tomcat
  sh ~/deploy/tomcat/stop.sh "$TOMCAT_HOME"  && \
  #update
  sh ~/deploy/tomcat/update.sh "$TOMCAT_HOME" "$APP_NAME" "$dir_update"  && \
  #startup_tomcat
  sh ~/deploy/tomcat/start.sh "$TOMCAT_HOME"  && \
  #url_check
  sh ~/deploy/common/url_check.sh "$CHECK_URL"
  ;;
rollback)
  #backup
   sh ~/deploy/common/backup.sh "$dir_src" "$dir_dest" "$APP_NAME"  && \
  #stop_tomcat
  sh ~/deploy/tomcat/stop.sh "$TOMCAT_HOME"  && \
  #update
  sh ~/deploy/tomcat/update.sh "$TOMCAT_HOME" "$APP_NAME" "$dir_update"  && \
  #startup_tomcat
  sh ~/deploy/tomcat/start.sh "$TOMCAT_HOME"  && \
  #url_check
  sh ~/deploy/common/url_check.sh "$CHECK_URL"
  ;;
*)
  usage
  ;;
esac
