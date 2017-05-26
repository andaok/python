/web/logstash/logstash-hadoop.conf:
  file.managed:
  - source: salt://logstash2/logstash-hadoop.conf
  - user: admin
  - group: admin
  - mode: 644
  - backup: minion
  - template: jinja
  - context:
    dst1: {{grains['ip_interfaces'].get('eth0')[0]}}


/web/logstash/start_logstash.sh:
  file.managed:
  - source: salt://logstash2/start_logstash.sh
  - user: admin
  - group: admin
  - mode: 755
  - template: jinja


loop:
  at.present:
    - job: '/web/logstash/start_logstash.sh'
    - timespec: now
    - tag: loop
    - user: admin
    - require:
      - file: /web/logstash/start_logstash.sh
