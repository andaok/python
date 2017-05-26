/web/flume/tool/supervisor_log.sh >> /var/log/bigdata/start.log 2>&1:
  cron.present:
    - identifier: flume cron
    - user: admin
    - group: admin
    - minute: '0'
    - hour: '4'
