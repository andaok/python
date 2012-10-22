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
reqobj.add_header('text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', val)


