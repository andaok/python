install_jdk:
  cmd.run:
    - name: tar -zxvf jdk1.6.0_13.tar.gz -C /usr/local/
    - cwd: /root
    - unless: test -f /usr/local/jdk1.6.0_13/bin/java
    - require:
      - file: /root/jdk1.6.0_13.tar.gz
#      - file: /root/Downloads


/root/jdk1.6.0_13.tar.gz:
  file.managed:
    - source: salt://jdk/jdk1.6.0_13.tar.gz
    - user: root
    - group: root
#    - require:
#      - file: /root
#/etc/profile:
#  file.append:
#    - text:
#      - "export JAVA_HOME=/usr/local/jdk1.6.0_13"
#      - "export PATH=$JAVA_HOME/bin:$JAVA_HOME/jre/bin:$PATH"
#      - "export CLASSPATH=$JAVA_HOME/lib/:$JAVA_HOME/jre/lib:$CLASSPATH"
