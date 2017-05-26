install_logstash:
  cmd.run:
    - name: tar -zxvf logstash-1.4.2.update-2015016.tar.gz -C /web/logstash/ && chown -R web:web /web/logstash
    - cwd: /root/Downloads
    - unless: test -f /web/logstash/logstash-1.4.2/bin/logstash
    - require:
      - file: /root/Downloads/logstash-1.4.2.update-2015016.tar.gz
      - file: /root/Downloads
      - file: /web/logstash


/root/Downloads/logstash-1.4.2.update-2015016.tar.gz:
  file.managed:
    - source: salt://logstashinstall/logstash-1.4.2.update-2015016.tar.gz
    - user: web
    - group: web
    - require:
      - file: /root/Downloads
/root/Downloads:
  file.directory:
    - user: root
    - group: root
    - file_mode: 644
    - dir_mode: 755
    - makedirs: True
    - include_empty: True
    - template: jinja
    - backup: minion
/web/logstash:
  file.directory:
    - user: web
    - group: web
    - file_mode: 644
    - dir_mode: 755
    - makedirs: True
    - include_empty: True
    - template: jinja
    - backup: minion
