#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ---------------------------/
# pycurl示例8
# pycurl实现post方法上传文件到服务端
# ---------------------------/


import os
import sys
import pycurl
import urllib2

class FileReader:
    def __init__(self,fp):
        self.fp = fp
    def read_callback(self,size):
        return self.fp.read(size)
    
url = "http://graph.cloudiya.com/wye.php"
#filename = "/var/data/github/BootStrap/html/test.txt"
filename = "/tmp/LICENSE.txt"


resp = urllib2.urlopen("http://graph.cloudiya.com/LICENSE.txt")

if not os.path.exists(filename):
    print("Error : the file '%s' does not exist"%filename)
    raise SystemExit

crl = pycurl.Curl()
crl.setopt(pycurl.VERBOSE,1)
crl.setopt(pycurl.URL,url)
crl.setopt(pycurl.UPLOAD,1)

if 1:
    #crl.setopt(pycurl.READFUNCTION,FileReader(open(filename,'rb')).read_callback)
    crl.setopt(pycurl.READFUNCTION,FileReader(resp.fp).read_callback)
else:
    #crl.setopt(pycurl.READFUNCTION,open(filename,'rb').read)
    crl.setopt(pycurl.READFUNCTION,resp.fp.read)
    
filesize = os.path.getsize(filename)

crl.setopt(pycurl.INFILESIZE,filesize)

#print("Uploading file %s to url %s"%(filename,url))

crl.perform()
crl.close()


