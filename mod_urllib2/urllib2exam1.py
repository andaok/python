#!/usr/bin/env python

# -*- encoding:utf-8 -*-

'''
Created on Jun 9, 2012

@author: wye

'''
import urllib2

#OPEN DEBUG MODEL
httpHandler = urllib2.HTTPHandler(debuglevel=1)
httpsHandler = urllib2.HTTPHandler(debuglevel=1)
opener = urllib2.build_opener(httpHandler,httpsHandler)
urllib2.install_opener(opener)

try:
    response = urllib2.urlopen("http://www.python.org/")
    #DISPLAY THE PAGE THE FIRST 100 BYTES
    print response.read(1000)
    print response.geturl()
    print response.getcode()
    print response.info()
except urllib2.HTTPError,e:
    #IF OPEN URL FAIL,PRINT HTTP RETURN CODE
    print e.code


