install_cmake:
  cmd.run:
    - name: tar -zxvf cmake-2.8.4.tar.gz && cd cmake-2.8.4 && sh configure && gmake && gmake install
    - cwd: /root/Downloads
    - unless: test -f /usr/local/bin/cmake
    - require:
      - file: /root/Downloads/cmake-2.8.4.tar.gz


/root/Downloads/cmake-2.8.4.tar.gz:
  file.managed:
    - source: salt://mysql/cmake-2.8.4.tar.gz
    - user: root
    - group: root
    - mode: 755
    - template: jinja

install_mysql:
  cmd.run:
    - name: useradd mysql && tar -zxvf mysql-5.5.27.tar.gz && cd mysql-5.5.27 && //usr/local/bin/cmake -DCMAKE_INSTALL_PREFIX=/web/mysql -DSYSCONFDIR=/web/mysql/etc -DMYSQL_DATADIR=/web/mysql/data -DMYSQL_TCP_PORT=3306 -DMYSQL_UNIX_ADDR=/tmp/mysqld.sock -DEXTRA_CHARSETS=all -DWITH_READLINE=1 -DWITH_SSL=system -DWITH_EMBEDDED_SERVER=1 -DENABLED_LOCAL_INFILE=1 -DWITH_INNOBASE_STORAGE_ENGINE=1 -DWITHOUT_PARTITION_STORAGE_ENGINE=1 && make && make install && cp /web/mysql/support-files/my-huge.cnf /etc/my.cnf &&  /web/mysql/scripts/mysql_install_db --user=mysql --basedir=/web/mysql --datadir=/web/mysql/data  && cp /web/mysql/support-files/mysql.server /etc/init.d/mysqld && cp /web/mysql/bin/* /sbin
    - cwd: /root/Downloads
    - unless: test -f /web/mysql/bin/mysql
    - require:
      - cmd: install_cmake
      - file: /root/Downloads/mysql-5.5.27.tar.gz

/root/Downloads/mysql-5.5.27.tar.gz:
  file.managed:
    - source: salt://mysql/mysql-5.5.27.tar.gz
    - user: root
    - group: root
    - mode: 755
    - template: jinja
