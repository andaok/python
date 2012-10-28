# -*- encoding:utf-8 -*-

'''
Created on 2012-10-28

@author: root
'''

"""
在多个线程里访问同一个队列对象
"""

import threading
import Queue
import time,random

WORKERS = 2

class Worker(threading.Thread):
    
    def __init__(self,queue):
        self.__queue = queue
        threading.Thread.__init__(self)
    
    def run(self):
        while 1:
            item = self.__queue.get()
            if item is None:
                break
            time.sleep(random.randint(10,100)/1000)
            print "task" , item ,"finished"

queue = Queue.Queue(0)

for i in range(WORKERS):
    Worker(queue).start()
    
for i in range(10):
    queue.put(i)

for i in range(WORKERS):
    queue.put(None)

