/web/logstash/logstash-hadoop.conf:
  file.managed:
  - source: salt://logstashmed66/logstash-hadoop.conf
  - user: admin
  - group: admin
  - mode: 644
  - backup: minion
  - template: jinja
  - context:
    dst1: {{grains['ip_interfaces'].get('eth0')[0]}}


#Run only if myscript changed something:
#  cmd.run:
#    - name: /web/logstash/logstash-1.4.2/bin/logstash agent -f /web/logstash/logstash-hadoop.conf &
#    - require:
#      - file: /web/logstash/logstash-hadoop.conf
