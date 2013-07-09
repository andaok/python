# -*- encoding:utf-8 -*-

'''
Created on 2012-10-28

@author: root
'''

"""
限制队列的大小，如果队列满了，那么控制主线程(threads producer)被阻塞,等待项目被弹出队列.
"""

import threading
import Queue
import time,random

WORKERS = 2

class Worker(threading.Thread):
    
    def __init__(self,queue,thname):
        self.__queue = queue
        self.__thname = thname
        threading.Thread.__init__(self)
        
    def run(self):
        while 1:
            item = self.__queue.get()
            if item is None:
                break
            #time.sleep(random.randint(10,100)/1000)
            time.sleep(2)
            print self.__thname,"task",item,"finished"
            
queue = Queue.Queue(3)

for i in range(WORKERS):
    Worker(queue,i+1).start()
    
for item in range(10):
    queue.put(item)
    print "push" , item
    
for i in range(WORKERS):
    queue.put(None)
    
