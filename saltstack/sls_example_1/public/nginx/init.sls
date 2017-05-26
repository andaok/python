include:
  - init_packages
  - create_user
install_nginx:
  cmd.run:
    - name: tar -zxvf nginx-1.4.5-1392172829533.tar.gz && cd nginx-1.4.5 && sh configure --prefix=/web/webserver/nginx --with-http_ssl_module && make && make install
    - cwd: /root/Downloads
    - unless: test -f /web/webserver/nginx/sbin/nginx
    - require:
      - sls: init_packages
      - file: /root/Downloads
      - file: /root/Downloads/nginx-1.4.5-1392172829533.tar.gz


/root/Downloads/nginx-1.4.5-1392172829533.tar.gz:
  file.managed:
    - source: salt://nginx/nginx-1.4.5-1392172829533.tar.gz
    - user: admin
    - group: admin
    - mode: 755
    - template: jinja
    - require:
      - file: /root/Downloads
      - sls: create_user

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
      - sls: create_user
