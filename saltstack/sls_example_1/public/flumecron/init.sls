/web/flume/log/log-statistic:
    file.directory:
    - source: salt://flumecron/log-statistic
    - template: jinja
    - user: admin
    - group: admin
/web/flume/log/log-statistic/ServerLogStatistic.jar:
    file.managed:
    - source: salt://flumecron/log-statistic/ServerLogStatistic.jar
    - template: jinja
    - user: admin
    - group: admin
    - require:
      - file: /web/flume/log/log-statistic
/web/flume/log/log-statistic/logfilepath.properties:
    file.managed:
    - source: salt://flumecron/log-statistic/logfilepath.properties
    - template: jinja
    - user: admin
    - group: admin
    - require:
      - file: /web/flume/log/log-statistic
/web/flume/log/log-statistic/flumecron.sh:
    file.managed:
    - source: salt://flumecron/flumecron.sh
    - template: jinja
    - user: admin
    - group: admin
    - mode: 777
    - require:
      - file: /web/flume/log/log-statistic
    cron.present:
      - minute: 30
      - hour: 1
