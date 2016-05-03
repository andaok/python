# -*- encoding:utf-8 -*-

from multiprocessing import Pool, Queue
import os
import sys
import time
import redis
import requests
import logging
import logging.handlers

queue = Queue(20)


RedisPool = redis.ConnectionPool(host='127.0.0.1',port=6379,db=0)
Redata = redis.Redis(connection_pool=RedisPool)

def GetLogger(logflag,loglevel="debug"):
    logger = logging.Logger(logflag)
    logfile = "/var/log/%s.log"%logflag
    hdlr = logging.handlers.RotatingFileHandler(logfile, maxBytes = 5*1024*1024, backupCount = 5)
    formatter = logging.Formatter("%(asctime)s -- [ %(name)s ] -- %(levelname)s -- %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)    
    if loglevel == "debug": 
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger

logger = GetLogger("pool")


def consumer():
    while True:
        try:
            k, url = Redata.blpop(['pool',])
            queue.put(url)
        except Exception,e:
            print "%s"%e

def worker():
    while True:
        url = queue.get()
        #print requests.get(url).text
        time.sleep(2)
        logger.info("%s"%os.getpid()+"-"+url)
        #print "%s"%(multiprocessing.current_process().name)+"-"+url

def process(ptype):
    try:
        if ptype:
            consumer()
        else:
            worker()
    except:
        pass

# pool = Pool(5)
# pool.map(process, [1,0,0,0,0])
# pool.close()
# pool.join()

if __name__ == "__main__":
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit first parent
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)
    # decouple from parent environment
    os.chdir("/")
    os.setsid() 
    os.umask(0) 
    # do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit from second parent, print eventual PID before
            #print "Daemon PID %d" % pid 
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1) 
    # start the daemon main loop
    try:
        pool = Pool(5)
        pool.map(process, [1,0,0,0,0])
        pool.close()
        pool.join()
    except Exception,e:
        print("Main Program Quit,Error is %s"%e)
        sys.exit()