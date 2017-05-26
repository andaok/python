/etc/security/limits.conf:
  file.managed:
    - source: salt://limits/limits.conf
    - user: root
    - group: root
    - mode: 644
    - template: jinja
/etc/security/limits.d/90-nproc.conf:
  file.managed:
    - source: salt://limits/90-nproc.conf
    - user: root
    - group: root
    - mode: 644
    - template: jinja
