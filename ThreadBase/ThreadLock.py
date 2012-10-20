# -*- encoding:utf-8 -*-

'''
Created on Sep 18, 2012

@author: root

write by wye in cloudiya
'''

import threading
import time

data = 0
lock = threading.Lock()

def func():
    global data
    print "%s acquire lock...." % threading.currentThread().getName()
    
    #调用acquire([timeout])时,线程将一直阻塞,直到获得锁定或者直到timeout秒后(timeout参数可选)
    
    if lock.acquire():
        print "%s get the lock." % threading.currentThread().getName()
        data += 1
        print data
        time.sleep(4)
        print "%s release lock ..." % threading.currentThread().getName()
        
        #调用release()将释放锁
        lock.release()
        
t1 = threading.Thread(target=func)
t2 = threading.Thread(target=func)
t3 = threading.Thread(target=func)

t1.start()
t2.start()
t3.start()

print data
    
