#include:
#  - init_packages
install_memcached:
  cmd.run:
    - name: tar -zxvf memcached-1.4.5.tar.gz && cd memcached-1.4.5 && sh configure --prefix=/usr/local/memcached  && make && make install
    - cwd: /root/Downloads
    - unless: test -f /usr/local/memcached/bin/memcached
    - require:
 #     - sls: init_packages
      - file: /root/Downloads/memcached-1.4.5.tar.gz

/root/Downloads/memcached-1.4.5.tar.gz:
  file.managed:
    - source: salt://memcached/memcached-1.4.5.tar.gz
    - user: root
    - group: root
    - mode: 755
    - template: jinja
