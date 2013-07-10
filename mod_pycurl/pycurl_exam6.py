#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ---------------------------/
# pycurl示例6
# pycurl实现post方法上传文件到服务端
# ---------------------------/
# $_POST 无法解释二进制流，需要用到 $GLOBALS['HTTP_RAW_POST_DATA'] 或 php://input
# $GLOBALS['HTTP_RAW_POST_DATA'] 和 php://input 都不能用于 enctype=multipart/form-data
# ---------------------------/

# -- /
# 服务端php代码
"""
<?php
 $data = file_get_contents("php://input");
 echo $data;
?>
"""
# -- /

import pycurl
import StringIO
import urllib

url = "http://graph.cloudiya.com/wye.php"

crl = pycurl.Curl()

#values = [("image",(pycurl.FORM_FILE,"/var/data/github/BootStrap/html/tmp.jpg"))]
values = [("html",(pycurl.FORM_FILE,"/var/data/github/BootStrap/html/demo1.html"))]
#values = [("name","jilly"),("age","10")]

crl.setopt(pycurl.VERBOSE,1)
crl.setopt(pycurl.CONNECTTIMEOUT,60)
crl.setopt(pycurl.TIMEOUT,300)

crl.fp = StringIO.StringIO()
crl.setopt(pycurl.USERAGENT,"Wye Browser")

crl.setopt(crl.HTTPPOST,values)

crl.setopt(crl.URL,url)
crl.setopt(crl.WRITEFUNCTION,crl.fp.write)

headers = ["Content-Type: application/x-www-form-urlencoded"] 
crl.setopt(crl.HTTPHEADER,headers)

crl.perform()

print(crl.fp.getvalue()) 

#respose data show 
"""
------------------------------965ac8803e38
Content-Disposition: form-data; name="name"

jilly
------------------------------965ac8803e38
Content-Disposition: form-data; name="age"

10
------------------------------965ac8803e38--
"""



