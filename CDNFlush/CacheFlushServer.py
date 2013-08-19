#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import ujson
import redis
from FlushClass import CDNFlush,GlobalConfig
from bottle import route,run,request,debug,static_file


Config = GlobalConfig()
CacheFlush = CDNFlush()

# --/
#     刷新CDN缓存
# --/

@route('/flushcdn',method='GET')
def flushcdn():
    
    redispool = redis.ConnectionPool(host=Config.redis_server_ip,port=Config.redis_server_port,db=Config.redis_db_name)
    redata = redis.Redis(connection_pool=redispool)
    
    urlstype = int(request.query.urlstype)
    RawUrls = request.query.urls
    UrlsList = RawUrls.split(",")
    
    urls = ""
    for url in UrlsList:
        urls = urls + url + "|"
    
    urls = urls[:-1] 
    
    receive_data_dict = CacheFlush.Flush(urls,urlstype)
    
    return request.query.jsoncallback + "(" + ujson.encode(receive_data_dict) + ")"

# --/
#     刷新SQUID缓存
# --/

@route('/flushsquid',method='GET')
def flushsquid():
    


debug(True)
run(host='192.168.0.111',port=8087)

