/usr/bin/jbossadm:
  file.managed:
    - source: salt://jbossadm/jbossadm
    - user: admin
    - group: admin
    - mode: 755
    - template: jinja

