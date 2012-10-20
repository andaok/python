# -*- encoding:utf-8 -*-

'''
Created on Sep 19, 2012

@author: root
'''
import threading
import time 
 
local = threading.local()
local.tname = 'main'
 
def func():
    local.tname = 'notmain'
    print local.tname

t1 = threading.Thread(target=func)
t1.start()
t1.join()
 
print local.tname