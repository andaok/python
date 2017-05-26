epel_install:
  file.managed:
    - name: /root/epel-release-6-8.noarch.rpm
    - source: salt://saltinit/epel-release-6-8.noarch.rpm
    - user: root
    - group: root
  cmd.run:
    - name: rpm -ivh /root/epel-release-6-8.noarch.rpm
    - unless: test -f /etc/yum.repos.d/epel.repo
    - require:
      - file: epel_install

salt_install:
  pkg.installed:
    - name: salt-minion
  file.managed:
    - name: /etc/salt/minion
    - source: salt://saltinit/minion
    - template: jinja
    - defaults:
      minion_id: {{grains['ip_interfaces'].get('eth0')[0]}}
  service.running:
    - name: salt-minion
    - enable: True
    - reload: True
    - watch:
      - file: salt_install
