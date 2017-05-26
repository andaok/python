#include:
#  - init_packages
php-install:
  cmd.run:
    - name: tar -jxvf php.tar.bz2 && cd php-5.4.2 && ./configure --prefix=/usr/local/php-fpm --enable-fpm --with-libdir=lib64 --with-bz2 --with-config-file-path=/usr/local/php-fpm/etc --with-config-file-scan-dir=/usr/local/php-fpm/etc/php.d --with-curl=/usr/local/lib --with-gd --with-gettext --with-jpeg-dir=/usr/local/lib --with-freetype-dir=/usr/local/lib --with-kerberos --with-mcrypt --with-mhash --with-mysql --with-mysqli --with-pcre-regex=/usr --with-pdo-mysql=shared --with-png-dir=/usr/local/lib --with-pspell --with-tidy --with-xmlrpc --with-xsl --with-zlib --with-zlib-dir=/usr/local/lib --with-openssl --with-iconv --enable-bcmath --enable-calendar --enable-exif --enable-ftp --enable-gd-native-ttf --enable-libxml  --enable-soap --enable-sockets --enable-mbstring --enable-zip --enable-wddx && make && make install 
    - cwd: /root/Downloads
    - unless: test -f /usr/local/php-fpm/sbin/php-fpm
    - require:
#      - sls: init_packages
      - file: /root/Downloads/php.tar.bz2
install-php-imagick:
  cmd.run:
    - name: /usr/local/php-fpm/bin/pecl install imagick
    - unless: test -f /usr/local/php-fpm/lib/php/extensions/no-debug-non-zts-20100525/imagick.so
    - require:
      - cmd: php-install
install-php-igbinary:
  cmd.run:
    - name: /usr/local/php-fpm/bin/pecl install igbinary
    - unless: test -f /usr/local/php-fpm/lib/php/extensions/no-debug-non-zts-20100525/igbinary.so
    - require:
      - cmd: php-install
install-php-mongo:
  cmd.run:
    - name: /usr/local/php-fpm/bin/pecl install mongo
    - unless: test -f /usr/local/php-fpm/lib/php/extensions/no-debug-non-zts-20100525/mongo.so
    - require:
      - cmd: php-install
install-php-libmemcached:
  cmd.run:
    - name: tar -zxvf libmemcached-1.0.16.tar.gz && cd libmemcached-1.0.16 && sh configure --prefix=/usr/local/libmemcached && make && make install
    - cwd: /root/Downloads
    - unless: test -f /usr/local/libmemcached/bin/memstat
    - require:
      - cmd: php-install
      - file: /root/Downloads/libmemcached-1.0.16.tar.gz

install-php-memcached:
  cmd.run:
    - name: tar -zxvf  memcached-2.1.0.tgz && cd memcached-2.1.0 && /usr/local/php-fpm/bin/phpize && sh configure --with-php-config=/usr/local/php-fpm/bin/php-config --enable-memcached-igbinary --with-libmemcached-dir=/usr/local/libmemcached && make && make install
    - cwd: /root/Downloads
    - unless: test -f /usr/local/php-fpm/lib/php/extensions/no-debug-non-zts-20100525/memcached.so
    - require:
      - cmd: install-php-libmemcached
    #  - cmd: install-php-igbinary
      - file: /root/Downloads/memcached-2.1.0.tgz

/etc/init.d/php-fpm:
  file.managed:
    - source: salt://php/php-fpm
    - user: root
    - group: root
    - mode: 755
    - template: jinja
    - backup: minion
    - require:
      - cmd: php-install
/usr/local/php-fpm/etc/php-fpm.conf:
  file.managed:
    - source: salt://php/php-fpm.conf
    - user: root
    - group: root
    - mode: 755
    - template: jinja
    - backup: minion
    - require:
      - cmd: php-install
/usr/local/php-fpm/etc/php.ini:
  file.managed:
    - source: salt://php/php.ini
    - user: root
    - group: root
    - mode: 755
    - template: jinja
    - backup: minion
    - require:
      - cmd: php-install
/root/Downloads/php.tar.bz2:
  file.managed:
    - source: salt://php/php.tar.bz2
    - user: root
    - group: root
    - mode: 755
    - template: jinja
/root/Downloads/memcached-2.1.0.tgz:
  file.managed:
    - source: salt://php/memcached-2.1.0.tgz
    - user: root
    - group: root
    - mode: 755
    - template: jinja
/root/Downloads/libmemcached-1.0.16.tar.gz:
  file.managed:
    - source: salt://php/libmemcached-1.0.16.tar.gz
    - user: root
    - group: root
    - mode: 755
    - template: jinja
