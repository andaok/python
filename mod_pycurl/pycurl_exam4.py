#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ---------------------------/
# pycurl示例4
# pycurl实现post方法
# ---------------------------/

# -- /
# 服务端php代码
"""
<?php
 echo "php format data is:\n";
 echo $_POST["name"]."\n";
 echo "post raw data is:\n";
 echo file_get_contents("php://input");
?>
"""
# -- /

import pycurl
import StringIO
import urllib

url = "http://graph.cloudiya.com/wye.php"
Post_Data_Dic = {"name":"jilly"}

crl = pycurl.Curl()
crl.setopt(pycurl.VERBOSE,1)
crl.setopt(pycurl.FOLLOWLOCATION,1)
crl.setopt(pycurl.MAXREDIRS,5)
crl.setopt(pycurl.CONNECTTIMEOUT,60)
crl.setopt(pycurl.TIMEOUT,300)
crl.setopt(pycurl.HTTPPROXYTUNNEL,1)

crl.fp = StringIO.StringIO()
crl.setopt(pycurl.USERAGENT,"Wye Browser")

crl.setopt(crl.POSTFIELDS,urllib.urlencode(Post_Data_Dic))

crl.setopt(pycurl.URL,url)
crl.setopt(crl.WRITEFUNCTION,crl.fp.write)

crl.perform()

print(crl.fp.getvalue()) 

# PRINT DATA SHOW 
"""
php format data is:
jilly
post raw data is:
name=jilly
"""


