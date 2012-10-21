# -*- encoding:utf-8 -*-

'''
Created on 2012-10-21

@author: root
'''

"""
Send a data-stream to the stdin of a CGI and reading the data it returns to us
"""

import urllib2

req = urllib2.Request(url='http://10.1.1.10/cgi-bin/test.cgi',data='this data is passed to stdin of the CGI')
f = urllib2.urlopen(req)

print f.read()

