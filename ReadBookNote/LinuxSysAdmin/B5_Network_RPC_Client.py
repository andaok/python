#-*- encoding:utf-8 -*-

'''
Created on 2012-11-18

@author: root
'''

import xmlrpclib

x = xmlrpclib.ServerProxy('http://127.0.0.1:8765')

print x.ls('.')

print x.ls('/tmp/')

print x.ls('/tmp/nodir')

print x.ls_boom('/tmp/nopdir')