# -*- encoding:utf-8 -*-

'''
Created on Sep 18, 2012

@author: root

write by wye in cloudiya
'''

import threading
import time

rlock = threading.RLock()

def func():
    #第一次请求锁定
    print "%s acquire lock first..." % threading.currentThread().getName()
    
    if rlock.acquire():
        print "%s get lock first..." % threading.currentThread().getName()
        
        time.sleep(4)
        
        #第二次请求锁定
        print "%s acquire lock second..." % threading.currentThread().getName()
        
        if rlock.acquire():
            print "%s get lock second..." % threading.currentThread().getName()
        
            time.sleep(4)
        
        #第一次释放锁
        print "%s release lock first..." % threading.currentThread().getName()
      
        rlock.release()
        time.sleep(4)
      
        #第二次释放锁
        print "%s release lock second..." % threading.currentThread().getName()
      
        rlock.release()
      
t1 = threading.Thread(target=func)
t2 = threading.Thread(target=func)
t3 = threading.Thread(target=func)

t1.start()
t2.start()
t3.start()

      
