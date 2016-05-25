#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Created on Jan 24, 2013

@author: wye

Copyright @ 2012 - 2013  Cloudiya Tech . Inc 

"""

"""
注意 ： 该脚本放置在red端,每日定时在23:00执行.

目的 ： 
       依据red中队列pendinglist,对还未处理的原始数据（客户端断电,断网,直接刷新页面,或是原始数据在转化成中间数据的过程失败造成的）进行处理生成中间数据存于redata中.
              
FAQ ：  
       red : 存储播放过程中产生的原始数据,有多个.
       redata :  存储原始数据转化来的中间数据

"""

import sys
import redis
import time
import ujson
import logging
import httplib

def getLog(logflag,logfile="/tmp/BatchPending.log",loglevel="info"):
    
    """Custom log objects"""
    
    logger = logging.Logger(logflag)
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter("%(asctime)s -- [ %(name)s ] -- %(levelname)s -- %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    
    if loglevel == "debug": 
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        
    return logger

redis_host = "127.0.0.1"
redis_port = 6379

web_host = "127.0.0.1"
web_port = "80"

play_expired_seconds = 24*60*60

try:
    
    logger = getLog("BatchPending")
    
    redispool = redis.ConnectionPool(host=redis_host,port=redis_port,db=0)
    redata = redis.Redis(connection_pool=redispool)
    
    list_length = redata.llen("pendinglist")
    
    if list_length == 0:
        logger.info("Pendinglist no data to handle")
    else:
        logger.info("Start handle data in pendinglist")
        
        data_list = redata.lrange("pendinglist",0,list_length-1)
        
        for key in data_list:
            
            if redata.exists(key+"_0") == True and redata.exists(key+"_Y") == True:
                
                """Obtain Client platform flag"""
                
                Key_Y_Value = ujson.decode(redata.get(key+"_Y"))
                
                if Key_Y_Value.has_key("flag"):
                    platflag = Key_Y_Value["flag"]
                else:
                    platflag = "win"
                    
                logger.info("Start handle key -- %s , Platform -- %s"%(key,platflag))
                
                play_starttime = ujson.decode(redata.get(key+"_0"))["starttime"]
                now_timestamp = int(time.time())
                
                if  now_timestamp - play_starttime > play_expired_seconds:
                    
                    """调用生成中间数据(vid_pid_S and vid_pid_J)处理接口"""
                    connection = httplib.HTTPConnection(web_host+":"+web_port)
                    
                    if platflag == "ios":
                        connection.request('GET',"/video?key=%s_C&value={wtime=%s,flag='ios'}"%(key,now_timestamp))
                    elif platflag == "win":
                        connection.request('GET',"/video?key=%s_C&value={wtime=%s}"%(key,now_timestamp))
                        
                    respmsg = connection.getresponse()
                    
                    if respmsg.status != 200:
                        logger.error("Call web api fail for key -- %s , Client platform  -- %s"%(key,platflag))
                        
            else:
                logger.error("%s is exist in pendinglist,but don't find it(%s,%s) in red"%(key,key+"_0",key+"_Y")) 
                
except Exception,e:
    logger.error("Program Exception : %s"%e)
    
    
    


