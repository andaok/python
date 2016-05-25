#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Created on Jan 9, 2013

@author: wye

Copyright @ 2012 - 2013  Cloudiya Tech . Inc 

"""

# --/
# 
#      HandleVidSet.py是整个批处理的第三步 
#      
#      处理方式：
#         依次处理redis中T_VIDS_$date集合中vid,处理完成一个删除一个.
#         如在该步出现异常终止,重新执行该步,直至T_VIDS_$date中所有vid条目执行完成后,再进入下一步.
#
#      依赖数据：
#         T_VIDS_$date
#         T_playtable_$date
#         T_loadtable_$date
#         T_regiontable_$date
#         T_IPS_$VID_$date
#         T_region_$vid_$date
#         T_region_$uid_$date
#
#       产生中间数据:
#         T_UIDS_$date
#
# --/

import sys
import redis
import Queue
import time
from PubMod import getLog
from PubMod import HandleConfig
from HandleAction import HandleUserinfo
from HandleAction import handleEndList
from HandleAction import handleTVIDSET
from HandleAction import handleTUIDSET
from HandleAction import writeData


# --/
#     基础数据是否存在于redis
# --/

def isExists(logger,redpipe,datadate):
    redpipe.exists("T_VIDS_%s"%datadate)
    
    for bvalue in redpipe.execute():
        if bvalue == False:
            return False
    return True


try:
    Config = HandleConfig()

    logger = getLog("Step3",logfile=Config.LogFile,loglevel=Config.LogLevel)
    
    logger.info("Step3 Handle Start")
    
    datadate = Config.date
    
    redispool = redis.ConnectionPool(host=Config.RedisIp,port=6379,db=0)
    redata = redis.Redis(connection_pool=redispool)
    redpipe = redata.pipeline() 
    
    if not isExists(logger,redpipe,datadate):
        logger.error("Does not satisfy the data processing requirements")
        sys.exit(Config.EX_CODE_3)
    
    queue = Queue.Queue(0)
    
    for i in range(Config.workers):
        worker_obj = handleTVIDSET(queue,logger,datadate,Config)
        worker_obj.setDaemon(True)
        worker_obj.start()
    
    for item in redata.smembers("T_VIDS_%s"%(datadate)):
        queue.put(item)
    
    queue.join()
    time.sleep(10)
 
    logger.info("Step3 Handle Complete")

except Exception,e:
    logger.error(e)
    sys.exit(Config.EX_CODE_3)