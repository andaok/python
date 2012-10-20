# -*- encoding:utf-8 -*-

'''
Created on Sep 19, 2012

@author: root

write by wye in cloudiya
'''

import threading

def func():
    print "hello timer"
    

timer = threading.Timer(5,func)

timer.start()

