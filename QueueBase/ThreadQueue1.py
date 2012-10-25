# -*- encoding:utf-8 -*-

'''
Created on Sep 20, 2012

@author: root

write by wye in cloudiya
'''

import Queue
import threading
import urllib2
import time

hosts = ["http://yahoo.com", "http://google.com.tw", "http://baidu.com","http://sina.com","http://126.com","http://yhetgame.com",
         "http://yahoo.com", "http://google.com", "http://amazon.com", "http://apple.com"]

queue = Queue.Queue()

class ThreadUrl(threading.Thread):
    
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self.queue = queue
        
    def run(self):
        while True:
            host = self.queue.get()
            
            url = urllib2.urlopen(host)
            print "start %s ..." % host
            print url.read(1024)
            
            self.queue.task_done()
            
start = time.time()

def main():
    
    for host in hosts:
        queue.put(host)
    
    for i in range(12):
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()
        
    queue.join()

main()

print "Elapsed Time: %s " % (time.time() - start)
            
            
            
            
            
            
            
            
            
            