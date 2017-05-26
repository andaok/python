/usr/local/rsyncdata.sh:
  file.managed:
  - source: salt://logstashscp/rsyncdata.sh
  - user: root
  - group: root
  - mode: 744
  - backup: minion
  - template: jinja

/tmp/mess.txt:
  file.managed:
  - source: salt://logstashscp/mess.txt
  - user: root
  - group: root
  - mode: 666
  - backup: minion
  - template: jinja
  - unless: test -f /tmp/mess.txt
