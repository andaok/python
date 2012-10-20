# -*- encoding:utf-8 -*-

'''
Created on Sep 18, 2012

@author: root

write by wye in cloudiya
'''

import threading
import time

def context(tjoin):
    print "in threadContext"
    tjoin.start()
    
    #将阻塞线程tcontext，直到线程tjoin终止
    tjoin.join()
    
    #tjoin终止后继续执行
    print "out threadContext"

def join():
    print "in threadJoin"
    
    time.sleep(2)
    
    print "out threadJoin"


tjoin = threading.Thread(target=join)
tcontext = threading.Thread(target=context,args=(tjoin,))

tcontext.start()    