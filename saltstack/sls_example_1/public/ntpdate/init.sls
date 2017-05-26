/usr/sbin/ntpdate time.windows.com:
  cron.present:
    - identifier: ntpdate rsync
    - user: root
    - minute: '*/30'
