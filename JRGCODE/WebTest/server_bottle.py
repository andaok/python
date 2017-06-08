#!/usr/bin/env python
# -*- encoding:utf-8 -*-*

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
from bottle import route,run,debug,request


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
    
    print("urls is : %s"%urls)
    
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

# ------------------------------------------------

@route('/test1',method="GET")
def test1():
    TestDict = {
        1:{"id":10454350,"name":"民生"},
        2:{"id":145431,"name":"工行"},
        3:{"id":1065785682,"name":"招行"}
    }

    return request.query.jsoncallback + "(" + ujson.encode(TestDict) + ")"

@route('/test2',method="GET")
def test2():
    prefix = request.query.jsoncallback
    action = request.query.action
    bankHandleString = request.query.bankHandleString
    print("action : %s \n bankHandleString : %s"%(action,bankHandleString))
    retdict = {"success":'0',"info":"hello"}
    return prefix+"("+ujson.encode(retdict)+")"

debug(True)    
run(host="0.0.0.0",port=8088)
