#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ---------------------------/
# pycurl示例5
# pycurl实现post方法
# ---------------------------/

# -- /
# 服务端php代码
"""
<?php
 $headers = getallheaders();
 print_r($headers);
 echo "post raw data is:\n";
 echo $GLOBALS["HTTP_RAW_POST_DATA"];
?>

"""
# -- /

import pycurl
import StringIO
import urllib

url = "http://graph.cloudiya.com/wye.php"
Post_Data_Dic = "my name is jilly"

crl = pycurl.Curl()
crl.setopt(pycurl.VERBOSE,1)
crl.setopt(pycurl.FOLLOWLOCATION,1)
crl.setopt(pycurl.MAXREDIRS,5)
crl.setopt(pycurl.CONNECTTIMEOUT,60)
crl.setopt(pycurl.TIMEOUT,300)
crl.setopt(pycurl.HTTPPROXYTUNNEL,1)

crl.fp = StringIO.StringIO()
crl.setopt(pycurl.USERAGENT,"Wye Browser")
crl.setopt(crl.POSTFIELDS,Post_Data_Dic)

crl.setopt(pycurl.URL,url)
crl.setopt(crl.WRITEFUNCTION,crl.fp.write)

#当请求的Content-Type不是application/x-www-form-urlencoded时,即php不能识别时,$HTTP_RAW_POST_DATA才会被赋值.
#headers = ["Content-Type: application/x-www-form-urlencoded"] 
headers = ["Content-Type: soap"] 
crl.setopt(crl.HTTPHEADER,headers)

crl.perform()

print(crl.fp.getvalue()) 

#respose data show
"""
Array
(
    [User-Agent] => Wye Browser
    [Host] => graph.cloudiya.com
    [Accept] => */*
    [Content-Type] => soap
    [Content-Length] => 16
)
post raw data is:
my name is jilly
"""


