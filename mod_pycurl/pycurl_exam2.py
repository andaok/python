#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ---------------------------/
# pycurl示例2
# ---------------------------/

import pycurl
import StringIO

url = "http://192.168.0.111:88/html/demo1.html"

crl = pycurl.Curl()
crl.setopt(pycurl.VERBOSE,0)
crl.setopt(pycurl.FOLLOWLOCATION,1)
crl.setopt(pycurl.MAXREDIRS,5)

crl.fp = StringIO.StringIO()

crl.setopt(pycurl.URL,url)
crl.setopt(pycurl.WRITEFUNCTION,crl.fp.write)
crl.perform()

print(crl.fp.getvalue())

