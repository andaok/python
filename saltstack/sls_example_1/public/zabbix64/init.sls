include:
  - create_user_zabbix
install_zabbix:
  cmd.run:
    - name: tar -zxvf zabbix_64.tar.gz -C /usr/local
    - cwd: /root/Downloads
    - unless: test -f /usr/local/zabbix/sbin/zabbix_server
    - require:
      - file: /root/Downloads
      - file: /root/Downloads/zabbix_64.tar.gz



/root/Downloads/zabbix_64.tar.gz:
  file.managed:
    - source: salt://zabbix64/zabbix_64.tar.gz
    - mode: 755
    - template: jinja
    - require:
      - file: /root/Downloads

/usr/local/zabbix/etc/zabbix_agentd.conf:
  file.managed:
  - source: salt://zabbix64/zabbix_agentd.conf
  - user: root
  - group: root
  - mode: 644
  - backup: minion
  - template: jinja
  - require:
    - file: /root/Downloads
    - cmd: install_zabbix 
  - context:
    dst1: {{grains['ip_interfaces'].get('eth0')[0]}}

/etc/init.d/zabbix_agentd:
  file.managed:
  - source: salt://zabbix64/zabbix_agentd
  - user: root
  - group: root
  - mode: 755
  - backup: minion
  - template: jinja

/root/Downloads:
  file.directory:
    - user: root
    - group: root
    - file_mode: 644
    - dir_mode: 644
    - makedirs: True
    - include_empty: True
    - template: jinja
    - backup: minion
