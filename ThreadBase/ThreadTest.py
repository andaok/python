# -*- encoding:utf-8 -*-

'''
Created on Sep 20, 2012

@author: root
'''

import threading
import time

def func(thread):
    print "start thread %s..." % threading.currentThread().getName()
    
    thread.join()
    
    
    
    
    