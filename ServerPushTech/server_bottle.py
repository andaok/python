'''
Created on 2013-8-17

@author: root
'''

import sys
import redis
import ujson
import time
import threading
import subprocess
from FlushClass import CDNFlush,GlobalConfig
from bottle import route,run,debug,request

Config = GlobalConfig()
CacheFlush = CDNFlush()

redispool = redis.ConnectionPool(host=Config.redis_server_ip,port=Config.redis_server_port,db=Config.redis_db_name)
redata = redis.Redis(connection_pool=redispool)

def exeCmd(keyname):
    proc = subprocess.Popen(['iostat','-d','-k','1','10'],stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        redata.rpush(keyname,line.rstrip())


@route('/flushsquid',method="GET")
def flushSquid():
    prefix = request.query.jsoncallback
    keyname = "key"+str(request.query.key)
    try:
        tobj = threading.Thread(target=exeCmd,args=(keyname,))
        tobj.start()
        DataDict =  {'success':'1'}
    except Exception,e:
        DataDict = {'success':'0','text':e}
    return prefix+"("+ujson.encode(DataDict)+")"


@route('/getstdout',method="GET")
def getStdout ():
    prefix = request.query.jsoncallback
    keyname = "key"+str(request.query.key)
    line = redata.blpop(keyname,10)
    if line == None:
        DataDict = {"success":'0'}
    else:
        DataDict = {"success":'1','text':line[1]}
    return prefix+"("+ujson.encode(DataDict)+")"
    sys.exit()


@route('/flushcdn',method='GET')
def flushcdn():
        
    urlstype = int(request.query.urlstype)
    RawUrls = request.query.urls
    UrlsList = RawUrls.split(",")
    
    urls = ""
    for url in UrlsList:
        urls = urls + url + "|"
    
    urls = urls[:-1] 
    
    receive_data_dict = CacheFlush.Flush(urls,urlstype)
    
    timestamp = int(time.time())
    
    if receive_data_dict["head"] == "success":
        redpipe = redata.pipeline()
        
        url_rid_pairs_list = receive_data_dict["body"]
        for item in url_rid_pairs_list:
            for url,rid in item.items():
                redpipe.zadd("CacheFlushingZSet",ujson.encode({rid:url}),timestamp)
                      
        redpipe.execute()
    
    return request.query.jsoncallback + "(" + ujson.encode(receive_data_dict) + ")"


@route('/flushinglist',method='GET')
def flushinglist():
    rid_url_pairs_dict = redata.zrange("CacheFlushingZSet",0,-1)
    print(ujson.encode(rid_url_pairs_dict))
    return request.query.jsoncallback + "(" + ujson.encode(rid_url_pairs_dict) + ")"


@route('/check',method="GET")
def check():
    RawRids = request.query.rids
    RidsList = RawRids.split(",")
    
    rids = ""
    for rid in RidsList:
        rids = rids + rid + "|"
    
    rids = rids[:-1] 
    
    receive_data_dict = CacheFlush.Check(rids)
    
    print(rids)
    
    return request.query.jsoncallback + "(" + ujson.encode(receive_data_dict) + ")"
    
    
@route('/waitflushlist',method="GET") 
def waitflushlist():
    start_position = int(request.query.sp)
    per_page_num = int(request.query.ppn)
    end_position = start_position + per_page_num - 1
    wait_flush_url_len = redata.llen("cacheurl_list")    
    wait_flush_url_list = redata.lrange("cacheurl_list",start_position,end_position)
    
    wait_flush_data_dict = {"urlsum":wait_flush_url_len,"urlsdata":wait_flush_url_list}
    
    print(ujson.encode(wait_flush_data_dict))
    return request.query.jsoncallback + "(" + ujson.encode(wait_flush_data_dict) + ")"
    
    
debug(True)    
run(host="0.0.0.0",port=8080)
