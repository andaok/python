#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pycurl
import cStringIO

# --/
#    结果输出到stdout即屏幕
# --/
def Test1():
    crl = pycurl.Curl()
    crl.setopt(pycurl.VERBOSE,1)
    crl.setopt(crl.URL,"http://graph.cloudiya.com/LICENSE.txt")


# --/
#    抓取输出,代替输出到stdout
# --/
def Test2():
    crl = pycurl.Curl()
    crl.setopt(pycurl.VERBOSE,1)
    crl.setopt(crl.URL,"http://graph.cloudiya.com/LICENSE.txt")

    buf = cStringIO.StringIO()
    crl.setopt(crl.WRITEFUNCTION,buf.write)
    crl.perform()
    print(buf.getvalue())
    
    buf.close()
    crl.close()

# --/
#   请求通过代理，设置连接和socket超时时间. 
# --/
def Test3():
    crl = pycurl.Curl()
    crl.setopt(pycurl.VERBOSE,1)
    crl.setopt(crl.URL,"http://graph.cloudiya.com/LICENSE.txt")
    crl.setopt(crl.CONNECTTIMEOUT,5)
    crl.setopt(crl.TIMEOUT,8)
    crl.setopt(crl.PROXY,"http://proxyserver.com:8088")

    buf = cStringIO.StringIO()
    crl.setopt(crl.WRITEFUNCTION,buf.write)
    crl.perform()
    print(buf.getvalue())
    
    buf.close()
    crl.close()

# --/
#    保持cookie会话, 复用连接.
#    This approach can be used to simulate, for example, 
#    login sessions or other flows throughout a web application that need multiple HTTP requests without having to bother with maintaining cookie (and also session cookie) state. 
#    Performing multiple HTTP requests on one cURL handle also has the convenient side effect that the TCP connection to the host will be reused when targeting the same host multiple times, 
#    which can obviously give you a performance boost.
# --/
def Test4():
    c = pycurl.Curl()
    c.setopt(c.URL, 'http://myappserver.com/ses1')
    c.setopt(c.COOKIEFILE, '')
    c.setopt(c.VERBOSE, True)
    c.perform()
 
    c.setopt(c.URL, 'http://myappserver.com/ses2')
    c.perform()

    
# --/
#     提供一定级别的容错能力
#     FAILONERROR : 
#     FAILONERROR cURL option to let cURL fail when a HTTP error code larger than or equal to 400 was returned. 
#     PycURL will throw an exception when this is the case, which allows you to gracefully deal with such situations.
# --/
def Test5():
    crl = pycurl.Curl()
    crl.setopt(crl.URL,'http://myappserver.com/ses1')
    crl.setopt(pycurl.CONNECTTIMEOUT,5)
    crl.setopt(pycurl.TIMEOUT,8)
    crl.setopt(pycurl.COOKIEFILE,'')
    crl.setopt(pycurl.FAILONERROR,True)
    crl.setopt(pycurl.HTTPHEADER,['Accept: text/html','Accept-Charset: UTF-8'])
    try:
        crl.perform()
        
        crl.setopt(pycurl.URL,'http://myappserver.com/ses2')
        crl.setopt(pycurl.POSTFIELDS,'foo=bar&bar=foo')
        crl.perform()
    except pycurl.error,error:
        print("An error occurred %s"%error)
        