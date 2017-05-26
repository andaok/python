include:
  - init_packages
install_cronolog:
  cmd.run:
    - name: tar -zxvf cronolog-1.6.2.tar.gz && cd cronolog-1.6.2 && sh configure  && make && make install
    - cwd: /root/Downloads
    - unless: test -f /usr/local/sbin/cronolog
    - require:
      - sls: init_packages
      - file: /root/Downloads/cronolog-1.6.2.tar.gz

/root/Downloads/cronolog-1.6.2.tar.gz:
  file.managed:
    - source: salt://cronolog/cronolog-1.6.2.tar.gz
    - user: root
    - group: root
    - mode: 755
    - template: jinja
