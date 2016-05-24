#!/usr/bin/env python
#-*- encoding:utf-8 -*-


# -----------------------------------------------
# Purpose:
#      Receive camera heatbeat packet,update camera status in redis.
# @author:wye
# @date:20151202
# @achieve basic functions
# -----------------------------------------------

import os
import sys
import time
import redis
import socket
import logging
import binascii
import logging.handlers
from cStringIO import StringIO

# ---------------------- /
# LOG FUNCTION
# ---------------------- /

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


# --------------------- /
# MAIN FUNCTION
# --------------------- /

def main(logger):
   
    host = "61.183.254.135"
    port = 5007
    redataIP = "10.2.10.19"
    redataPort = 6379
    redataDB = 0

    #host = "192.168.0.111"
    #port = 5007
    #redataIP = "192.168.0.111"
    #redataPort = 6379
    #redataDB = 0

    redispool = redis.ConnectionPool(host=redataIP,port=redataPort,db=redataDB)    
    redata = redis.Redis(connection_pool=redispool)

    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((host,port))

    while True:
        data,addr=s.recvfrom(192)
        #logger.debug("%s"%binascii.b2a_hex(data))        
        if not data:
            logger.error("Don't Contain HeartBeat Data ,Continue......")
            continue
        OriDataBuf = StringIO(data)
        OriDataBuf.read(128)
        Cid = OriDataBuf.read(8)
        IPAddr =  addr[0]
        TimeStamp = int(time.time())

        #logger.debug("%s-%s"%(Cid,IPAddr))

        # -------------------
        # OriDataBuf.read(24)
        # Yid = OriDataBuf.read(7)
        # -------------------

        if len(Cid) == 8:
            try:
                DataMap = {"time":TimeStamp,"WanIPFromCam":IPAddr}
                redata.hmset("%s_status"%Cid,DataMap)
            except Exception,e:
                logger.error("Write Data To Redis Failure,Error Is %s,Main Program Not Quit..."%e)
        else:
            logger.error("Cid Format Is Invaild,Cid Is %s"%Cid)

    s.close()


if __name__ == "__main__":
    logger = GetLogger("CamHBChecK")
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
        main(logger)
    except Exception,e:
        logger.error("Main Program Quit,Error is %s"%e)
        sys.exit()

