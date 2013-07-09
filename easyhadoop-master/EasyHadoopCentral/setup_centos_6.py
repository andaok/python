#!/usr/bin/python
# -*- coding: utf8 -*-
import os
import pickle
import random

class Token:
	def __init__(self):
		self.token = ''
	
	def CreateToken(self):
		self.token = str(random.randint(2000000000, 9000000000));
		if(os.path.isfile('/usr/local/ehm_agent/authenticate.key')) == False:
			try:
				file = open('/usr/local/ehm_agent/authenticate.key', 'wb')
				pickle.dump(self.token, file)
				print "The token is %s , please remember it and write it down." % self.token
				file.close()
				return self.token
			except IOError, e:
				return '{"Exception":"' + e + '"}'
		else:
			try:
				file = open('/usr/local/ehm_agent/authenticate.key', 'rb')
				self.token = pickle.load(file)
				print "The token is " + self.token + " , please remember it and write it down."
				file.close()
				return self.token
			except IOError, e:
				return '{"Exception":"' + e + '"}'

repo = 'http://42.96.141.99/'

os.system('yum install -y php php-cli php-devel php-common httpd httpd-devel php-mbstring php-mysql php-pdo php-process mysql mysql-devel mysql-server mysql-libs wget lrzsz dos2unix pexpect libxml2 libxml2-devel MySQL-python curl curl-devel')
os.system('/sbin/service mysqld start')
os.system('mysql -hlocalhost -uroot -e"create database if not exists easyhadoop"')
os.system('mysql -hlocalhost -uroot --default-character-set=utf8 easyhadoop < easyhadoop.sql')
os.system('mysql -hlocalhost -uroot --default-character-set=utf8 easyhadoop < patch-0001.sql')
os.system('mysql -hlocalhost -uroot --default-character-set=utf8 easyhadoop < patch-0002.sql')
os.system('mysql -hlocalhost -uroot --default-character-set=utf8 easyhadoop < patch-0003.sql')

print "/*************************************************************/"
print "Install basic environment complete, starting download from"
print "EasyHadoop repositry......"
print "/*************************************************************/"

os.system('mkdir -p ./hadoop')
#os.system('rm -f ./hadoop/*')
if(os.path.isfile('./hadoop/centos_6.bin')) == False: #hadoop-1.1.2-1
	os.system('wget '+repo+'centos_6.bin -P ./hadoop/')
if(os.path.isfile('./NodeAgent-1.2.0-1.x86_64.rpm')) == False:
	os.system('wget '+repo+'/agent/NodeAgent-1.2.0-1.x86_64.rpm')

os.system('rpm -Uvh ./NodeAgent-1.2.0-1.x86_64.rpm')
os.system('cp -R * /var/www/html')
os.system('/sbin/service httpd start')
os.system('echo "service httpd start" >> /etc/rc.local')
os.system('echo "service mysqld start" >> /etc/rc.local')
os.system('echo "python /usr/local/ehm_agent/NodeAgent.py -s restart" >> /etc/rc.local')
os.system('/sbin/service iptables stop')
os.system('/sbin/chkconfig --del iptables')
print "/*************************************************************/"
print "Download Hadoop installation and runtime libaries complete."
print "Generate token key..."
token = Token()
t = token.CreateToken()
print "token key complete"
print "Generate /var/www/html/config.inc.php..."
config_php = ''
config_php += '<?php\n\n'
config_php += '#this is user definable area\n#这里是用户定义区域\n'
config_php += '$configure[\'language\'] = \'english\';\n\n'
config_php += '$configure[\'packages_source_address\'] = \'42.96.141.99\';\n\n'
config_php += '$configure[\'token\'] = \'%s\';\n\n' % t
config_php += '?>'
filename = '/var/www/html/config.inc.php'
f = open(filename, 'w')
f.write(config_php)
f.close()
print '/var/www/html/config.inc.php complete'
print "Access EasyHadoopCentral from your web browser."
print "/*************************************************************/"
