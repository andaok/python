# -*- encoding:utf-8 -*-

'''
Created on 2012-10-21

@author: root
'''

"""
Send a data-stream to the stdin of a CGI and reading the data it returns to us
"""

import urllib2

#OPEN DEBUG MODEL
httpHandler = urllib2.HTTPHandler(debuglevel=1)
httpsHandler = urllib2.HTTPHandler(debuglevel=1)
opener = urllib2.build_opener(httpHandler,httpsHandler)
urllib2.install_opener(opener)

req = urllib2.Request(url='http://10.1.1.10/cgi-bin/test.cgi',data='this data is passed to stdin of the CGI')
f = urllib2.urlopen(req)

print f.read()

#CGI PROGRAM
#!/usr/bin/env python
#import sys
#data = sys.stdin.read()
#print 'Content-type: text-plain\n\nGot Data: "%s"' % data
