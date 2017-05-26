include:
  - create_user_zabbix
install_zabbix:
  cmd.run:
    - name: tar -zxvf zabbix-2.4.6.tar.gz && cd zabbix-2.4.6 && sh configure --prefix=/usr/local/zabbix --enable-agent && make && make install
    - cwd: /root/Downloads
    - unless: test -f /usr/local/zabbix/sbin/zabbix_server
    - require:
      - file: /root/Downloads
      - file: /root/Downloads/zabbix-2.4.6.tar.gz


/root/Downloads/zabbix-2.4.6.tar.gz:
  file.managed:
    - source: salt://zabbix/zabbix-2.4.6.tar.gz
    - mode: 755
    - template: jinja
    - require:
      - file: /root/Downloads

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
    - require:
      - sls: create_user_zabbix
