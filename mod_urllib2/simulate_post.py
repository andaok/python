#! -*- encoding:utf-8 -*-

'''
Created on 2012-10-23

@author: wye
'''

"""
Simulate post data to web server
"""

import urllib2


reqobj = urllib2.Request(url='http://10.1.1.10/upload.php')
reqobj.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0.4) Gecko/20120425 Firefox/10.0.4')
reqobj.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
reqobj.add_header('Accept-Language', 'zh-cn,zh;q=0.5')
reqobj.add_header('Accept-Encoding', 'gzip,deflate')
reqobj.add_header('Connection', 'keep-alive')
reqobj.add_header('Content-Type', 'multipart/form-data; boundary=---------------------------976794555999887760121093636')
reqobj.add_header('Content-Length', '49020')

f = open('/tmp/github.log','r')
data = f.read()
f.close()

boundaryflag="---------------------------976794555999887760121093636"

