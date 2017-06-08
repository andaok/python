#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------
# @Date    : 2016-12-09 22:02:35
# @Author  : wye
# @Version : v1.0
# @Descr   : server side for web tool set
# -------------------------------------

import os
import sys
import redis
import time
import ujson
import urllib2
import logging
import logging.handlers
from bottle import route,run,debug,request

# ----------------
# API INTERFACE
# ----------------

# UFO UAT ENV
UFO_BANK_API_IP = "172.99.245.68"
UFO_BANK_API_PORT = 8080


# ----------------
# REDIS
# ----------------
RedisIP = "172.99.28.31"
RedisPort = 6379
RedisDB = 0


# ----------------
# FUNCTIONS
# ----------------

def GetLogHandler(logflag,loglevel="debug"):
    logger = logging.Logger(logflag)
    logfile = "/var/log/%s.log"%logflag
    hdlr = logging.handlers.RotatingFileHandler(logfile, maxBytes = 5*1024*1024, backupCount = 5)
    formatter = logging.Formatter("%(asctime)s -- [ %(name)s ] -- %(levelname)s -- %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)    
    if loglevel == "debug": 
        logger.setLevel(logging.DEBUG)
    elif loglevel == "info":
        logger.setLevel(logging.INFO)
    elif loglevel == "warning":
        logger.setLevel(logging.WARNING)
    elif loglevel == "error":
        logger.setLevel(logging.ERROR)
    elif loglevel == "critical":
        logger.setLevel(logging.CRITICAL)
    return logger

logger = GetLogHandler("WebToolSet")

# --------------------

def CallUFOBankApi(action,BankHandleString):
    """
    Call ufo api to start or stop bank service 
    """
    
    data = {
            'bankHandleString': BankHandleString
           }
    
    req = urllib2.Request('http://%s:%s/api/others/%s'%(UFO_BANK_API_IP,UFO_BANK_API_PORT,action))
    req.add_header('Content-Type', 'application/json')
    req.add_header('client_id', 'APP')
    response = urllib2.urlopen(req, ujson.encode(data))
    return response.read()


def WriteDataToRedisList(ListName,data):
    """
    Write data to list of redis list type
    """
    redispool = redis.ConnectionPool(host=RedisIP,port=RedisPort,db=RedisDB)
    redata = redis.Redis(connection_pool=redispool)
    redata.lpush(ListName,data)


@route('/GetBankExecHistory',method="GET")
def GetBankExecHistory():
    """
    Get operate history records from redis, and 
    Return it to web side. 
    """
    redispool = redis.ConnectionPool(host=RedisIP,port=RedisPort,db=RedisDB)
    redata = redis.Redis(connection_pool=redispool)
    TmpDict=redata.lrange("BankExecHisInfo",0,-1)
    return request.query.jsoncallback + "(" + ujson.encode(TmpDict) + ")"
    

@route('/GetBankInfo',method="GET")
def GetBankInfo():
    InfoDict = {
        1:{"code":111,"name":"工商银行"},
        2:{"code":112,"name":"中国农业银行"},
        3:{"code":123,"name":"中国银行"},
        4:{"code":114,"name":"建设银行"},
        5:{"code":115,"name":"中信银行"},
        6:{"code":116,"name":"光大银行"},
        7:{"code":117,"name":"民生银行"},
        8:{"code":118,"name":"广发银行"},
        9:{"code":119,"name":"平安银行"},
        10:{"code":120,"name":"招商银行"},
        11:{"code":121,"name":"交通银行"}
    }

    return request.query.jsoncallback + "(" + ujson.encode(InfoDict) + ")"


@route('/SendBankInfoToServer',method="GET")
def SendBankInfoToServer():
    """
    (1) Receive data from web side,call api interface,
    (2) Call api interface
    (3) Return data to web side
    """

    try:
        prefix = request.query.jsoncallback
        action = request.query.action
        BankHandleString = request.query.bankHandleString
        HandleDesrcStr = request.query.HandleDesrcStr

        RetInfoJson = CallUFOBankApi(action,BankHandleString)
        RetInfoDict = ujson.decode(RetInfoJson)
        resCode = RetInfoDict["resCode"]

        ExecTime = time.strftime('%Y-%m-%d %H:%M:%S')

        TmpDict = {
             "ExecTime":ExecTime,
             "action":action,
             "BankHandleString":BankHandleString,
             "HandleDesrcStr":HandleDesrcStr,
             "resCode":resCode
        }

        WriteDataToRedisList("BankExecHisInfo",ujson.encode(TmpDict))
        return prefix+"("+RetInfoJson+")"

    except Exception,e:
        logger.debug("Have Exception,Error is : \n %s"%e)


if __name__ == "__main__":
    # do the UNIX double-fork magic, see Stevens' "Advanced 
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
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
            print "Daemon PID %d" % pid 
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1) 
    # start the daemon main loop
    run(host="0.0.0.0",port=8089)

