supervisor:
  pkg.installed
/etc/supervisord.conf:
  file.managed:
    - source: salt://supervisor/supervisord.conf
    - user: root
    - group: root
    - mode: 644
    - backup: minion
    - template: jinja
supervisord-start:
  cmd.run:
    - name: /usr/bin/supervisord -c /etc/supervisord.conf
    - require:
      - file: /etc/supervisord.conf 
