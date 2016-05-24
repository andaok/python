#! /usr/bin/env python 
# -*- encoding:utf-8 -*-

# ---------------------------------------------------  /
#
# Create On 2016-01-12
# Author : wye
# Copyright @ 2015 - 2016  Cloudiya Tech.Inc
#
# -----------------------------
#
#处理原始考勤信息.
#如果考勤机绑定了摄像头，则处理生成对应考勤视频,最后将包含考勤视频m3u8文件名的考勤信息写入下一个管道.
#如考勤机没有绑定摄像头，则直接将原始考勤信息直接写入下一个管道.
#
# -----------------------------
#
#@Date:2016-01-12
#@Complete base functions
#@Date:2016-03-10
#@将老师考勤信息导入到新的队列
#
# ----------------------------------------------------  /


import os
import re
import sys
import time
import redis
import httplib
import logging
import logging.handlers
from multiprocessing import Pool, Queue

redataIP = "10.2.10.19"
redataPort = 6379
redataDB = 0

OriAttenListName = "OriAttenDataList"
NewAttenListName = "AttenDataList"
NewTeachAttenListName = "TeachAttenDataList"

queue = Queue(20)

# ----------------------- /
# CACHE ATTENANCE DEVICE BIND INFO IN LOCAL
# CACHE DATA FORMAT,AS FOLLOWS:
# {"812100001":"JFKL25-C3vwnP04-10.2.10.30",....}
# ----------------------- /
AttenDev_Bind_Info_Dict = {}

# ----------------------- /
# LOG FUNCTION
# ----------------------- /
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

logger = GetLogger("CreateAttenVideo")

RedisPool = redis.ConnectionPool(host=redataIP,port=redataPort,db=redataDB)
Redata = redis.Redis(connection_pool=RedisPool)


# ----------------------- /
# GET ORIGIAL ATTENANCE DATA FROM REDIS,PUT ITS TO QUEUE. 
# ----------------------- /
def GetOriAttenInfo():
    while True:
        try:
            key, atten = Redata.blpop([OriAttenListName,])
            queue.put(atten)
        except Exception,e:
            logger.error("Get Origial Atten Data Exception,Error is %s,But Program Does Not Exit...."%e)

        
# ----------------------- /
# GET ATTENANCE DEVICE BIND INFO FROM REDIS
# ----------------------- /
def GetBindInfoFromRedis(AttenDevID):
    try:
        KeyValue = Redata.hget("kqj_bind_info",AttenDevID)
        if KeyValue == None:
            return None
        else:
            return KeyValue
    except Exception,e:
        return None


# ----------------------- /
# WRITE ATTENANCE DATA TO NEW PIPE,WAIT FOR NEXT HANDLE.
# ----------------------- /
def WriteAttenToNewPipe(atten):
    try:
        AttenCardID = atten.split("-")[2].lstrip("0")
        if re.match("9[0-9]{7}$",AttenCardID):
            Redata.rpush(NewTeachAttenListName,atten)
        else:
            Redata.rpush(NewAttenListName,atten)
    except Exception,e:
        logger.error("Write Atten Data To New Pipe Fail, Atten Data is : %s"%atten)


# ---------------------- /
# ORIGIAL ATTENANCE DATA WRITE BACK ORIGIAL ATTEN LIST
# ---------------------- /
def WriteOriAttenToOriPipe(atten):
    try:
        Redata.rpush(OriAttenListName,atten)
    except Exception,e:
        logger.error("Write Back Origial Atten Data To Old Pipe Fail, Atten Data is : %s"%atten)


# ---------------------- /
# FUNCTION DESCRIPTION:
#    REMOTE CALL HTTP API INTERFACE FOR CREATE ATTENANCE VIDEO,
#    IF SUCCESS TO RETURN M3U8 FILE NAME.
# HTTP RESPONSE FOR SUCCESS AS FOLLOWS:
#    {"status":0,"info":"201512150389803899.m3u8"}
# HTTP RESPONSE FOR FAILURE AS FOLLOWS:
#    {"status":1,"info":"Parameters Format Error"}
#    {"status":1,"info":"Video Not Found"}
#    {"status":2,"info":"Video Files Are Being Generated"}
# ---------------------- /
def CallCreateVideoApi(oid,cid,cjs_ip,AttenTime,port=81):
    httpClient = None
    try:
        httpClient = httplib.HTTPConnection(cjs_ip,port,timeout=2)
        httpClient.request('GET', '/getplaylist/%s/%s/%s'%(oid,cid,AttenTime))
        response = httpClient.getresponse()
        if response.status == 200:
            info_dict = eval(response.read())
            if int(info_dict['status']) == 0:
                M3u8FileName = info_dict['info']
                return M3u8FileName
            else:
                logger.warning("UrlPath : http://%s:%s/%s/%s/%s , Api Response : %s"%(cjs_ip,port,oid,cid,AttenTime,info_dict))
                return None
        else:
            return None
    except Exception,e:
        logger.error("Create Video Fail In Call API Interface,Error info : %s"%e)
        return None
    finally:
        if httpClient:
            httpClient.close()


# ----------------------- /
# MAIN PROGRAM FOR CREATE ATTENANCE VIDEO
# ----------------------- /
def GenVideoByAtten(atten):
    try:
        AttenSegList = atten.split("-")
        AttenDevID,AttenTime,AttenCardID = AttenSegList[0],AttenSegList[1],AttenSegList[2]
        if int(time.time()) - int(AttenTime)  > 40:
            # Atten Device Bind Info In Local Program Cache
            if AttenDev_Bind_Info_Dict.has_key(AttenDevID):
                AttenDevBindSegList = AttenDev_Bind_Info_Dict[AttenDevID].split("-")
                oid,cid,cjs_ip = AttenDevBindSegList[0],AttenDevBindSegList[1],AttenDevBindSegList[2]
                M3u8FileName = CallCreateVideoApi(oid,cid,cjs_ip,AttenTime)
                if M3u8FileName != None:
                    NewAtten = atten + "-" + M3u8FileName
                    WriteAttenToNewPipe(NewAtten)
                else:
                    WriteAttenToNewPipe(atten)
            else:
                # Don't Find Atten Device Bind Info In Local Program Cache,Get It From Redis.
                AttenDevBindInfo = GetBindInfoFromRedis(AttenDevID)
                if AttenDevBindInfo != None:
                    AttenDev_Bind_Info_Dict[AttenDevID] = AttenDevBindInfo
                    AttenDevBindSegList = AttenDevBindInfo.split("-")
                    oid,cid,cjs_ip = AttenDevBindSegList[0] ,AttenDevBindSegList[1] ,AttenDevBindSegList[2]
                    M3u8FileName = CallCreateVideoApi(oid,cid,cjs_ip,AttenTime)
                    if M3u8FileName != None:
                        NewAtten = atten + "-" + M3u8FileName
                        WriteAttenToNewPipe(NewAtten)
                    else:
                        WriteAttenToNewPipe(atten)
                else:
                    # The Atten Device Don't Bind Any Camera,Direct Write Origial Atten Data To Next Pipe.
                    WriteAttenToNewPipe(atten)
        else:
            WriteOriAttenToOriPipe(atten)
    except Exception,e:
        logger.error("Have Exception,But Don't Exit,Error is %s"%e)
        

# ----------------------- /
# WORK PROCESS
# ----------------------- /
def worker():
    while True:
        atten = queue.get()
        GenVideoByAtten(atten)

# ----------------------- /
# TASK SCHEDULING
# ----------------------- /
def process(ptype):
    try:
        if ptype:
            GetOriAttenInfo()
        else:
            worker()
    except:
        logger.error("Have Exception,But Don't Exit,Error is %s"%e)


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
        logger.error("Main Program Quit,Error is %s"%e)
        sys.exit()



















