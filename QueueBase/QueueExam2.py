'''
Created on 2012-10-28

@author: root
'''

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
            time.sleep(random.randint(10,100)/1000)
            print self.__thname,"task",item,"finished"
            
queue = Queue.Queue(3)

for i in range(WORKERS):
    Worker(queue,i+1).start()
    print i
    
for item in range(10):
    queue.put(item)
    print "push" , item
    
for i in range(WORKERS):
    queue.put(None)
