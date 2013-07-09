# -*- encoding:utf-8 -*-

'''
Created on Sep 20, 2012

@author: root
'''
import Queue
import threading
class Job(object):
    def __init__(self,priority,description):
        self.priority=priority
        self.description=description
        print 'New Job:',description
        return
    def __cmp__(self, other):
        return cmp(self.priority,other.priority)
q=Queue.PriorityQueue()
q.put(Job(3,'Middle Level Job.'))
q.put(Job(10,'Low Level Job.'))
q.put(Job(1,'High Level Job.'))

def process_job(q):
    while True:
        next_job=q.get()
        print 'processing job:',next_job.description
        q.task_done()
workers=[threading.Thread(target=process_job,args=(q,)),
         threading.Thread(target=process_job,args=(q,)),]
for w in workers:
    w.setDaemon(True)
    w.start()
q.join()
