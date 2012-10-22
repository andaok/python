#! -*- encoding:utf-8 -*-

'''
Created on 2012-10-23

@author: wye
'''

"""
Simulate post data to web server
"""

import urllib2

#OPEN DEBUG MODEL
httpHandler = urllib2.HTTPHandler(debuglevel=1)
httpsHandler = urllib2.HTTPHandler(debuglevel=1)
opener = urllib2.build_opener(httpHandler,httpsHandler)
urllib2.install_opener(opener)


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

senddata=""
senddata = senddata+boundaryflag
senddata = senddata+"\r\n"
senddata = senddata+"Content-Disposition:form-data;name='file';filename='xiha.txt'"
senddata = senddata+"\r\n"
senddata = senddata+"Content-Type:text/plain"
senddata = senddata+"\r\n"
senddata = senddata+data
senddata = senddata+boundaryflag+"--"
senddata = senddata+"\r\n"

reqobj.add_data(senddata)

response = urllib2.urlopen(reqobj)

print response.info()
