# -*- encoding:utf-8 -*-

'''
Created on Sep 20, 2012

@author: root
'''

import urllib2
import time
        
hosts = ["http://yahoo.com", "http://google.com.tw", "http://baidu.com","http://sina.com","http://126.com","http://yhetgame.com",
         "http://yahoo.com", "http://google.com", "http://amazon.com", "http://apple.com"]

        
start = time.time()

#grabs urls of hosts and prints first 1024 bytes of page
for host in hosts:
    url = urllib2.urlopen(host)
    print url.read(1024)
        
print "Elapsed Time: %s" % (time.time() - start)
