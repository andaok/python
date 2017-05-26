install_tomcat:
  cmd.run:
    - name: tar -zxvf apache-tomcat-7.0.56.tar.gz -C /web/webserver/tomcat/ && chown -R admin:admin /web/webserver/tomcat/apache-tomcat-7.0.56
    - cwd: /root/Downloads
    - unless: test -f /web/webserver/tomcat/apache-tomcat-7.0.56/bin/startup.sh
    - require:
      - file: /root/Downloads/apache-tomcat-7.0.56.tar.gz
      - file: /web/webserver/tomcat


/root/Downloads/apache-tomcat-7.0.56.tar.gz:
  file.managed:
    - source: salt://tomcat/apache-tomcat-7.0.56.tar.gz
    - user: admin
    - group: admin
    - mode: 755
/web/webserver/tomcat/apache-tomcat-7.0.56/bin/catalina.sh:
  file.managed:
    - source: salt://tomcat/catalina.sh
    - user: admin
    - group: admin
    - mode: 755
    - require:
      - cmd: install_tomcat
      - file: /root/Downloads/apache-tomcat-7.0.56.tar.gz
/web/webserver/tomcat/apache-tomcat-7.0.56/conf/server.xml:
  file.managed:
    - source: salt://tomcat/server.xml
    - user: admin
    - group: admin
    - mode: 644
    - require:
      - cmd: install_tomcat
      - file: /root/Downloads/apache-tomcat-7.0.56.tar.gz

/web/webserver/tomcat:
  file.directory:
    - user: admin
    - group: admin
    - file_mode: 644
    - dir_mode: 755
    - makedirs: True
    - include_empty: True
    - template: jinja
    - backup: minion
