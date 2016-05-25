#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Created on Jan 9, 2013

@author: wye

Copyright @ 2012 - 2013  Cloudiya Tech . Inc 

"""

"""
注意 ： 该脚本定时在每天00：00点执行

目的 ： 
       (1)依据redata中队列endlist,处理redata中vid_pid_S和vid_pid_J

FAQ ：  
       red : 存储播放过程中产生的原始数据,有多个.
       redata :  存储原始数据转化来的中间数据

涉及到的数据结构：
             loadtable : 哈希表 ： 存储所有视频每天载入次数 ： 程序开始运行时将其数据copy到T_loadtable_$date并将其清零
             playtable : 哈希表 ： 存储所有视频每天播放次数 ： 程序开始运行时将其数据copy到T_playtable_$date并将其清零
           regiontable : 哈希表 ： 存储了所有视频和用户的地域载入次数 ： 程序开始运行时将其数据copy到T_regiontable_$date并将其清零 
               endlist : 队列   : 存储每天正常播放完成的播放信息 ： 程序开始运行时将其数据copy到T_endlist_$date并将其清零
             errorlist : 队列   : 存储每天播放过程中产生的错误信息 : 程序完成后清零
      T_IPS_$vid_$date : 集合   : 帮助统计视频每天独立IP个数 : 程序开始时建立,完成后销毁.
          T_VIDS_$date : 集合   : 帮助统计每天有数据变动的视频 ： 程序开始时建立,完成后销毁.
          T_UIDS_$date : 集合   : 帮助统计每天有数据变动的用户 :  程序开始时建立,完成后销毁.
T_engagesum_$uid_$date : 哈希表 ： 帮助统计每天该用户下uid,vid,kid完成率之和  : 程序开始时建立,完成后销毁.
            vid_playid : 哈希表 ： 存储所有视频自增ID值 : 永不销毁 , 备份存于mondodb
   T_region_$vid_$date : 集合   : 存储了每一个视频的每天的播放地域 ：开始时候建立，完成后销毁
   T_region_$uid_$date : 集合   : 存储了每一个用户每天的播放地域   ：开始时候建立，完成后销毁
   T_regiontable_$date : 哈希表 :  存储了所有视频和用户的地域载入次数   ：开始时候建立，完成后销毁     
"""

import sys
import redis
import ujson
import json
import time
import Queue
import threading
import datetime
import logging
import operator
import MySQLdb
from pymongo import MongoClient

from UserInfo import UidInfo
from UserInfo import KidInfo
from UserInfo import VidInfo
from WebHdfsAPI import WebHadoop
from PubMod import mergerPlaySeg
from xml.etree import ElementTree as ET


city_dir = {"Anhui" : "01",
            "Zhejiang" : "02",
            "Jiangxi" : "03",
            "Jiangsu" : "04",
            "Jilin" : "05",
            "Qinghai" : "06",
            "Fujian" : "07",
            "Heilongjiang" : "08",
            "Henan" : "09",
            "Hebei" : "10",
            "Hunan" : "11",
            "Hubei" : "12",
            "Xinjiang" : "13",
            "Xizang" : "14",
            "Gansu" : "15",
            "Guangxi" : "16",
            "Guizhou" : "18",
            "Liaoning" : "19",
            "Neimenggu" : "20",
            "Ningxia" : "21",
            "Beijing" : "22",
            "Shanghai" : "23",
            "Shanxi" : "24",
            "Shandong" : "25",
            "Shaanxi" : "26",
            "Tianjin" : "28",
            "Yunnan" : "29",
            "Guangdong" : "30",
            "Hainan" : "31",
            "Sichuan" : "32",               # 四川
            "Chongqing" : "33",             # 重庆
            "HongKong" : "34",              # 香港
            "Macau" : "35",                 # 澳门
            "Taiwan" : "36",                # 台湾
            "Diaoyudao" : "37",             # 钓鱼岛
            "Nanhai" : "38",                # 南海
            "Foreign" : "39",               # 国外
            }

city_list = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","18","19","20","21","22","23","24","25","26","28","29","30","31","32","33","34","35","36","37","38","39"]

# --/
#     日志
# --/

def getLog(logflag,logfile="/tmp/BatchPro.log",loglevel="info"):
    
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

# --/
#     运行该脚本的基础数据是否存在于redis
# --/

def isExists(logger,redpipe):
    redpipe.exists("loadtable")
    redpipe.exists("playtable")
    redpipe.exists("endlist")
    redpipe.exists("regiontable")
    for bvalue in redpipe.execute():
        if bvalue == False:
            return False
    
    return True

# --/
#     重新命名基础数据key名称
# --/

def handleInit(redpipe):
    redpipe.multi()
    
    redpipe.renamenx("loadtable","T_loadtable_%s"%(datadate))
    redpipe.renamenx("playtable","T_playtable_%s"%(datadate))
    redpipe.renamenx("endlist","T_endlist_%s"%(datadate))
    redpipe.renamenx("regiontable","T_regiontable_%s"%(datadate))

# -- /
#      删除redis中临时数据
# -- /

def delTmpData(redata):
    keylist = redata.keys("T_*")
    
    redpipe = redata.pipeline()
    for key in keylist:
        redpipe.delete(key)
    redpipe.execute()
    
# --/
#     插入当天的数据到uid_rdata中
# --/

class HandleUserinfo(threading.Thread):
    def __init__(self,queue,logger,datadate,Config):
            
        self.queue = queue
            
        self.log = logger
            
        self.datadate = datadate
            
        self.redataIP = Config.RedisIp
            
        threading.Thread.__init__(self)
        
    def run(self): 
        try:
            redispool = redis.ConnectionPool(host=self.redataIP,port=6379,db=0)
            redata = redis.Redis(connection_pool=redispool)            
        except Exception,e:
            self.log.error("connect to redis except :%s" % e)         
        while True:
            uid = self.queue.get()
            UidKey = "%s_rdate" % str(uid)
            try:
                redata.rpush(UidKey,self.datadate)
                self.queue.task_done()
            except Exception,e:
                self.log.error("insert into uid_rdata exception: %s" % e)
            

class HandleConfig(object):
    
    def __init__(self):
        self.MongodbIp = "192.168.0.203"
        
        self.MongodbPort = 27017
        
        self.MysqldbIp = "192.168.0.112"
        
        self.MysqldbPort = 3306
        
        self.MysqlUser = "cloudiya"
        
        self.MysqlPassword = "c10udiya"
        
        self.MysqlDbname = "video"
        
        self.RedisIp = "192.168.0.111"
        
        self.RedisPort = 6379
        
        self.HdfsHost = "192.168.0.112"
        
        self.HdfsPort = 50071
        
        self.HdfsUser = "cloudiyadatauser"
        
        self.HdfsPrefix="/webhdfs/v1"

# --/
#     处理endlist中N次完整播放过程数据
# --/

class handleEndList(threading.Thread):
    
    """ Handle vid_pid stored in endlist"""
    
    def __init__(self,queue,logger,datadate,Config):
        
        self.queue = queue
        
        self.log = logger
        
        self.datadate = datadate
        
        self.redataIP = Config.RedisIp
        
        self.mongodbIP = Config.MongodbIp
        
        self.mysqlIP = Config.MysqldbIp
        self.mysqlPort = Config.MysqldbPort
        self.mysqlUser = Config.MysqlUser
        self.mysqlPassword = Config.MysqlPassword
        self.mysqlDbname = Config.MysqlDbname
        
        threading.Thread.__init__(self)
        
    def run(self):
            
        redispool = redis.ConnectionPool(host=self.redataIP,port=6379,db=0)
        redata = redis.Redis(connection_pool=redispool) 
        
        mongoconn = MongoClient(self.mongodbIP,27017)
        
        date = self.datadate
        
        while True:
            
            """KeyName Format : vid_pid"""
            KeyName = self.queue.get()            
            vid = KeyName[0:7]
            uid = vid[0:4]

            """Obtain kid for the vid"""
            kid = redata.hget("T_video_kid_info",vid)
            
            if kid == None:
                "Obtain kid for the vid from mysql db"
                sql = '''
                        select b.kid from vinfo as a left join vsort as b on a.vsortid = b.id where a.vid = %s          
                      '''
                mysql_conn = MySQLdb.connect(host=self.mysqlIP,user=self.mysqlUser,passwd=self.mysqlPassword,port=self.mysqlPort,db=self.mysqlDbname,charset="utf8")
                cursor = mysql_conn.cursor()            
                param = vid
                n = cursor.execute(sql,param)
                if n == 1:
                    kid = cursor.fetchall()[0][0]
                    if kid == None:kid = "nokid"        
                    redata.hset("T_video_kid_info",vid,kid)
                    
            print "the %s kid is %s" % (vid,kid)
                
            """Obtain play data for the 'KeyName'"""
            redpipe = redata.pipeline()
            redpipe.get(KeyName+"_S")
            redpipe.get(KeyName+"_J")
            PlayDataList = redpipe.execute()
            
            """Base data for this a play"""            
            starttime = ujson.decode(PlayDataList[0])["starttime"]
            
            country = ujson.decode(PlayDataList[0])["country"]
            region = str(ujson.decode(PlayDataList[0])["region"])
            city = ujson.decode(PlayDataList[0])["city"]
            
            ip = ujson.decode(PlayDataList[0])["ip"]
            os = ujson.decode(PlayDataList[0])["os"]
            browser = ujson.decode(PlayDataList[0])["browser"]
            
            flow = float(ujson.decode(PlayDataList[0])["flow"])
            comprate = float(ujson.decode(PlayDataList[0])["comprate"])
            
            interdata = ujson.decode(PlayDataList[1])
            
            playdata = [[int(i[0])*2-2,int(i[0])*2,int(i[1])] for i in interdata]
            
            playdata = mergerPlaySeg(playdata)
            
            """Temp data write to redis"""
            redpipe = redata.pipeline()
            """ip for every play daily,but No duplicate ip"""
            """for the number of statistically independent ip"""
            redpipe.sadd("T_IPS_"+vid+"_%s"%(date),ip)
            """To facilitate the processing of the video data changs"""
            redpipe.sadd("T_VIDS_%s"%(date),vid)
            """To facilitate the processing of the video access region"""
            redpipe.sadd("T_region_%s_%s"%(vid,date),region)
            redpipe.sadd("T_region_%s_%s"%(uid,date),region)
            redpipe.execute()
            
            
            """--开始--"""
            
            # --/
            #     建立mongodb表连接
            # --/
            
            uid_stat_t =  mongoconn["video"]["%s_stat"%(uid)]
            vid_play_t =  mongoconn["video"]["%s_play"%(vid)]
            uid_vdaily_t = mongoconn["video"]["%s_vdaily"%(uid)]
            uid_daily_t = mongoconn["video"]["%s_daily"%(uid)]
            uid_type_t = mongoconn["video"]["%s_type"%(uid)]
            
            request = mongoconn.start_request()
            
            # --/
            #     为加快计算,将视频,用户,类别的每天的完成率和写到redis
            # --/
            #
            redpipe = redata.pipeline()
            redpipe.hincrbyfloat("T_engagesum_%s_%s"%(uid,date),vid,float(comprate))
            redpipe.hincrbyfloat("T_engagesum_%s_%s"%(uid,date),uid,float(comprate))
            if kid != "nokid" :
                redpipe.hincrbyfloat("T_engagesum_%s_%s"%(uid,date),kid,float(comprate))
            redpipe.execute()
           
            # --/
            #     统计视频每次播放信息
            # --/
            
            """获取该vid自增长id值"""
            
            if not redata.hexists("vid_playid",vid):     
                """读mongodb数据库video表uid_stat获取该vid自增长id值"""
                tmpval = uid_stat_t.find_one({"_id":vid},{"_id":0,"PlayID":1})
                if tmpval == None or len(tmpval) == 0:
                    playid = redata.hincrby("vid_playid",vid,1)
                else:
                    playid = int(tmpval["PlayID"])+1
                    redata.hset("vid_playid",vid,playid)
            else:
                playid = redata.hincrby("vid_playid",vid,1)
                
            """statistics of a play for the vid"""
            vid_play_t.update({"_id":int(playid)},{"$set":{
                                                           "PlayTime":starttime,
                                                           "PIP":ip,
                                                           "Engage":comprate,
                                                           "Country":country,
                                                           "Provinces":region,
                                                           "PGeo":city,
                                                           "Htmap":ujson.encode(playdata),
                                                           "OS":os,
                                                           "Browser":browser
                                                           }},upsert=True,w=0)
            
            # --/
            #     统计视频每天播放信息
            # --/
            
            """total flow for the vid daily"""
            """region distribution for the vid daily""" 
            
            uid_vdaily_t.update({"_id":date},{"$inc":{
                                                      "%s.Traffic"%(vid):flow,
                                                      "%s.Geo.%s.ClickNum"%(vid,region):1,
                                                      "%s.Geo.%s.Load"%(vid,region):0,
                                                      "%s.Geo.%s.Traffic"%(vid,region):flow,
                                                      "%s.Geo.%s.EngageSum"%(vid,region):comprate,
                                                      "%s.EngageSum"%(vid):comprate
                                                      }},upsert=True,w=0)
                                                    
                                                    
            # --/
            #     统计视频截至到目前总的播放信息
            # --/
            
            """flow of the total for the vid up to now"""
            """region distribution for the vid up to now"""
            """average complete rate sum of the vid up to now"""
            
            uid_stat_t.update({"_id":vid},{"$inc":{
                                                   "Traffic":flow,
                                                   "Geo.%s.ClickNum"%(region):1,
                                                   "Geo.%s.Load"%(region):0,
                                                   "Geo.%s.Traffic"%(region):flow,
                                                   "Geo.%s.EngageSum"%(region):comprate,
                                                   "EngageSum":comprate
                                                   }},upsert=True,w=0)
            
            """interactive data(time point) of total for the vid up to now"""
            
            for interseg in interdata:
                uid_stat_t.update({"_id":vid},{"$inc":{"HeatMapSum.%s"%(str(interseg[0])):interseg[1],"PlayMapSum.%s"%(str(interseg[0])):1}},upsert=True,w=0)
                    
            # --/
            #     统计用户每天播放信息
            # --/
            
            """total flow for the uid daily"""
            """region distribution for the uid daily""" 
            
            uid_daily_t.update({"_id":date},{"$inc":{
                                                     "Traffic":flow,
                                                     "Geo.%s.ClickNum"%(region):1,
                                                     "Geo.%s.Load"%(region):0,
                                                     "Geo.%s.Traffic"%(region):flow,
                                                     "Geo.%s.EngageSum"%(region):comprate,
                                                     "EngageSum":comprate
                                                     }},upsert=True,w=0)
                
            # --/
            #     统计用户截至到目前总的播放信息
            # --/           
           
            """flow of the total for the uid up to now"""
            """region distribution for the uid up to now"""
            
            uid_stat_t.update({"_id":uid},{"$inc":{
                                                   "Traffic":flow,
                                                   "Geo.%s.Load"%(region):0,
                                                   "Geo.%s.ClickNum"%(region):1,
                                                   "Geo.%s.Traffic"%(region):flow,
                                                   "Geo.%s.EngageSum"%(region):comprate,
                                                   "Mtraffic":flow,
                                                   "EngageSum":comprate
                                                   }},upsert=True,w=0)
                       
            # --/
            #     统计用户类别每天播放信息
            # --/
            
            """total flow for the uid's kid daily"""
            """region distribution for the uid's kid daily"""
            if kid != "nokid":
                uid_type_t.update({"_id":date},{"$inc":{
                                                    "%s.Traffic"%(kid):flow,
                                                    "%s.Geo.%s.ClickNum"%(kid,region):1,
                                                    "%s.Geo.%s.Load"%(kid,region):0,
                                                    "%s.Geo.%s.Traffic"%(kid,region):flow,
                                                    "%s.Geo.%s.EngageSum"%(kid,region):comprate,
                                                    "%s.EngageSum"%(kid):comprate
                                                    }},upsert=True,w=0)
           
            # --/
            #     统计用户类别截至到目前总的播放信息
            # --/
            
            """flow of the total for the uid's kid up to now"""
            """region distribution for the uid's kid up to now"""
            #if kid:
            #    uid_stat_t.update({"_id":kid},{"$inc":{"Traffic":flow,"Geo.%s.ClickNum"%(region):1,"Geo.%s.Load"%(region):0,"Geo.%s.Traffic"%(region):flow,"Geo.%s.EngageSum"%(region):comprate,"EngageSum":comprate}},upsert=True,w=0)
            
            request.end()
            
            """--结束--"""
            
            self.queue.task_done()


# --/
#     处理"T_VIDS_$date"中vid数据
# --/

class handleTVIDSET(threading.Thread):
    
    """handle vid stored in T_VIDS_$date"""

    def __init__(self,queue,logger,datadate,Config):
        
        self.queue = queue
                
        self.log = logger
                
        self.datadate = datadate                
        self.redataIP = Config.RedisIp
                
        self.mongodbIP = Config.MongodbIp
        self.mysqlIP = Config.MysqldbIp           
        self.mysqlPort = Config.MysqldbPort
        self.mysqlUser = Config.MysqlUser
        self.mysqlPassword = Config.MysqlPassword
        self.mysqlDbname = Config.MysqlDbname            
            
        threading.Thread.__init__(self)
    
    
    
    def run(self):
        
        redispool = redis.ConnectionPool(host=self.redataIP,port=6379,db=0)
        redata = redis.Redis(connection_pool=redispool) 
        
        mongoconn = MongoClient(self.mongodbIP,27017)
                
        date = self.datadate
        
        while True:
            try:
                
                """Obtain vid name for have data changs daily"""
                vid = self.queue.get()
                                                
                """Obtain uid for the vid"""
                uid = vid[0:4]
                
                print("handleTVIDSET -- Handling is %s"%vid)
                
                """Obtain video time from redis db for the vid """
                videoinfo = redata.get("%s_info"%vid)
                if videoinfo == None:
                    #Get from mysql
                    videotime = 1770
                else:
                    videotime = json.loads(videoinfo)['duration']
                    
                """Obtain kid from redis db for the vid"""
                kid = redata.hget("T_video_kid_info",vid)
    
                """Obtain temp data from redis"""
                redpipe = redata.pipeline()
                """Obtain the number of independent IP for the vid daily"""
                redpipe.scard("T_IPS_"+vid+"_%s"%(date))
                """Obtain load numbers for the vid daily"""
                redpipe.hget("T_loadtable_%s"%(date),vid)
                """Obtain play numbers for the vid daily"""
                redpipe.hget("T_playtable_%s"%(date),vid)
                """Write uid to set for facilitate the processing after"""
                redpipe.sadd("T_UIDS_%s"%(date),uid)
                vidDataList = redpipe.execute()

                indepipnums = int(vidDataList[0])
                dailyload =  int(vidDataList[1])
                dailyplay =  int(vidDataList[2])
                
                                
                """--开始--"""
                
                # --/
                #     建立mongodb表连接
                # --/
                
                uid_stat_t =  mongoconn["video"]["%s_stat"%(uid)]
                uid_vdaily_t = mongoconn["video"]["%s_vdaily"%(uid)]
                uid_daily_t = mongoconn["video"]["%s_daily"%(uid)]
                uid_type_t = mongoconn["video"]["%s_type"%(uid)]
                
                request = mongoconn.start_request()
                
                # --/
                #     保存该视频playid去mongodb
                # --/
                
                playid = redata.hget("vid_playid",vid)
                
                print(playid)
                
                uid_stat_t.update({"_id":vid},{"$set":{"PlayID":int(playid)}},upsert=True,w=0)
                
                # --/
                #     统计视频每天播放信息
                # --/
                
                """total loads of the vid daily"""
                """total plays of the vid daily"""
                """average click rate of the vid daily"""
                """the number of independent IP for the vid daily"""
                """avarage complete rate for the vid daily"""
                
                uid_vdaily_t.update({"_id":date},{"$set":{
                                                          "%s.Load"%(vid):dailyload,
                                                          "%s.Play"%(vid):dailyplay,
                                                          "%s.Click"%(vid):operator.itruediv(dailyplay, dailyload),
                                                          "%s.IP"%(vid):indepipnums,
                                                          "%s.Engage"%(vid):operator.itruediv(float(redata.hget("T_engagesum_%s_%s"%(uid,date),vid)),dailyplay)
                                                         }},upsert=True,w=0)
                                
                

                # --/
                #     统计视频截至到目前总的播放信息
                # --/
                
                """Load nums of total for the vid up to now"""
                """play nums of total for the vid up to now"""
                """independent IPs of total for the vid up to now"""
                
                uid_stat_t.update({"_id":vid},{"$inc":{
                                                       "Load":dailyload,
                                                       "Play":dailyplay,
                                                       "IP":indepipnums
                                                       }},upsert=True,w=0)
                
                region_list = list(redata.smembers("T_region_%s_%s"%(vid,date)))
                
                for i in region_list:
                    LoadSum = redata.hget("T_regiontable_%s"%(date),"%s%s"%(vid,i))
                    uid_stat_t.update({"_id":vid},{"$inc":{
                                                        "Geo.%s.Load"%(i):int(LoadSum)
                                                        }},upsert=True,w=0)
                                                        
                                                        
                    uid_vdaily_t.update({"_id":date},{"$inc":{
                                                        "%s.Geo.%s.Load"%(vid,i):int(LoadSum)
                                                        }},upsert=True,w=0)    
                                    
                
                """获取目前为止该视频总的载入数,播放数和每次播放完成率之和"""
                res = uid_stat_t.find_one({"_id":vid},{"_id":0,"Load":1,"Play":1,"EngageSum":1})
                vidtotalload = int(res["Load"])
                vidtotalplay = int(res["Play"])
                videngagesum = float(res["EngageSum"])
                
                """准备数据为计算截至目前该视频播放的交互记录"""
                def returnVal(dict,key):
                    if dict.has_key(key):
                        return dict[key]
                    else:
                        return 0
                                
                TotalSegFlagDict = uid_stat_t.find_one({"_id":vid},{"_id":0,"HeatMapSum":1})["HeatMapSum"]
                                
                totalinterdata = [[int(k)*2-2,int(k)*2,int(v)] for k,v in TotalSegFlagDict.items()]
                
                totalinterdata.sort()
                
                print("prehandle hmap is : ",ujson.encode(totalinterdata))
                
                totalinterdata = mergerPlaySeg(totalinterdata)
                
                print("befhandle hmap is : ",ujson.encode(totalinterdata))
                
                
                """
                if operator.mod(videotime, 2) != 0:videotime = videotime + 1
                
                ptmplist = [0,0,returnVal(totaltimepointdict,"0")]
                
                for i in range(2,videotime+2,2):
                    
                    if returnVal(totaltimepointdict,"%s"%(i)) == returnVal(totaltimepointdict,"%s"%(i-2)):
                        ptmplist[1] = i   
                    else:
                        totalinterdata.append(ptmplist)
                        ptmplist = [i,i,returnVal(totaltimepointdict,"%s"%(i))]
                                  
                totalinterdata.append(ptmplist)
                
                for playseg in totalinterdata:
                    if playseg[2] == 0:
                        totalinterdata.remove(playseg)
                """
                
                
                totalplayhotpointdict = uid_stat_t.find_one({"_id":vid},{"_id":0,"PlayMapSum":1})["PlayMapSum"]
                
                totalplayhotdata = [[int(k)*2-2,int(k)*2,int(v)] for k,v in totalplayhotpointdict.items()]
                
                totalplayhotdata.sort()
                
                print("prehandle pmap is : ",ujson.encode(totalplayhotdata))
                
                totalplayhotdata = mergerPlaySeg(totalplayhotdata)
                
                print("prehandle pmap is : ",ujson.encode(totalplayhotdata))
                
                """
                if operator.mod(videotime, 2) != 0:videotime = videotime + 1
                                
                phottmplist = [0,0,returnVal(totalplayhotpointdict,"0")]
                                
                for i in range(2,videotime+2,2):
                                    
                    if returnVal(totalplayhotpointdict,"%s"%(i)) == returnVal(totalplayhotpointdict,"%s"%(i-2)):
                        phottmplist[1] = i   
                    else:
                        totalplayhotdata.append(phottmplist)
                        phottmplist = [i,i,returnVal(totalplayhotpointdict,"%s"%(i))]
                                                  
                totalplayhotdata.append(phottmplist)
                                
                for playseg in totalplayhotdata:
                    if playseg[2] == 0:
                        totalplayhotdata.remove(playseg)       
                """        
                                 
                
                """average click rate of total for the vid up to now"""
                """average complete rate of total for the vid up to now"""
                """interactive data(time segment) of total for the vid up to now"""
                
                uid_stat_t.update({"_id":vid},{"$set":{
                                                       "Click":operator.itruediv(vidtotalplay,vidtotalload),
                                                       "Engage":operator.itruediv(videngagesum,vidtotalplay),
                                                       "Htmap":ujson.encode(totalinterdata),
                                                       "Ptmap":ujson.encode(totalplayhotdata)
                                                       }},upsert=True,w=0)
                
                
                print "Ptmap finished......"
                
                # --/
                #     统计用户每天的播放信息
                # --/
                
                """Load nums for the uid daily"""
                """play nums for the uid daily"""
                """the number of independent IP for the uid daily"""
                
                uid_daily_t.update({"_id":date},{"$inc":{"Load":dailyload,"Play":dailyplay,"IP":indepipnums}},upsert=True,w=0)
                
                
                # --/
                #     统计用户截至目前的播放信息
                # --/
                
                """Load nums of total for the uid up to now"""
                """play nums of total for the uid up to now"""
                """independent IPs of total for the uid up to now"""
                
                uid_stat_t.update({"_id":uid},{"$inc":{"Load":dailyload,"Play":dailyplay,"IP":indepipnums}},upsert=True,w=0)
                
                
                # --/
                #     统计用户类别每天播放信息
                # --/
                                
                """Load nums for the uid's kid daily"""
                """play nums for the uid's kid daily"""
                """the number of independent IP for the uid's kid daily"""
                if kid != "nokid":
                    uid_type_t.update({"_id":date},{"$inc":{"%s.Load"%(kid):dailyload,"%s.Play"%(kid):dailyplay,"%s.IP"%(kid):indepipnums}},upsert=True,w=0)
                   
                # --/
                #     统计用户类别截至目前播放信息
                # --/
                                
                """Load nums of total for the uid's kid up to now"""
                """play nums of total for the uid's kid up to now"""
                """independent IPs of total for the uid's kid up to now"""
                if kid != "nokid":
                    for i in region_list:
                        LoadSum = redata.hget("T_regiontable_%s"%(date),"%s%s"%(vid,i))            
                        uid_type_t.update({"_id":date},{"$inc":{
                                                        "%s.Geo.%s.Load"%(kid,i):int(LoadSum)
                                                        }},upsert=True,w=0)        
                request.end()
                
                """--结束--"""
                print "vid handle finish...."  
                             
                self.queue.task_done()
                
            except Exception,e:
                
                self.log.error("handleTVIDSET -- handle -- exception,%s"%(e))
                
                break
                

# --/
#     处理"T_UIDS_DATE"中uid
# --/
                               
class handleTUIDSET(threading.Thread):
     
    """handle uid stored in T_UIDS"""
    def __init__(self,queue,logger,datadate,Config):
        
        self.queue = queue
        self.log = logger
                
        self.datadate = datadate
        self.redataIP = Config.RedisIp
                
        self.mongodbIP = Config.MongodbIp   
        self.mysqlIP = Config.MysqldbIp
        self.mysqlPort = Config.MysqldbPort
        self.mysqlUser = Config.MysqlUser
        self.mysqlPassword = Config.MysqlPassword
        self.mysqlDbname = Config.MysqlDbname           

        threading.Thread.__init__(self)       
    
    def run(self):
        
        redispool = redis.ConnectionPool(host=self.redataIP,port=6379,db=0)
        redata = redis.Redis(connection_pool=redispool) 
        
        mongoconn = MongoClient(self.mongodbIP,27017)
        
        date = self.datadate        
                
        while True:
            try:
                
                """Obtain uid name for have data changs daily"""
                uid = self.queue.get()
                
                print(uid)
                
                """Obtain video nums from redis db for the uid"""                
                uidvideonums = len(redata.keys("%s???_info"%uid))
                                       
                """--开始--"""
                
                # --/
                #     建立mongodb表连接
                # --/
                
                uid_stat_t =  mongoconn["video"]["%s_stat"%(uid)]
                uid_vdaily_t = mongoconn["video"]["%s_vdaily"%(uid)]
                uid_daily_t = mongoconn["video"]["%s_daily"%(uid)]
                uid_type_t = mongoconn["video"]["%s_type"%(uid)]
                
                request = mongoconn.start_request()
                
                # --/
                #     统计用户每天播放信息
                # --/
                
                print "uid handel ready to go...."
                
                """获取用户视频该天载入次数,播放次数"""
                uiddailystat = uid_daily_t.find_one({"_id":date},{"_id":0,"Load":1,"Play":1})
                uiddailyload = int(uiddailystat["Load"])
                uiddailyplay = int(uiddailystat["Play"])
                
                """video nums for the uid"""
                """average complete rate for the uid daily"""
                """Calculate avarge click rate for the uid daily"""
                
                uid_daily_t.update({"_id":date},{"$set":{
                                                         "Nvideo":uidvideonums,
                                                         "Engage":operator.itruediv(float(redata.hget("T_engagesum_%s_%s"%(uid,date),uid)),uiddailyplay),
                                                         "Click":operator.itruediv(uiddailyplay,uiddailyload)
                                                        }},upsert=True,w=0)
                
                
                # --/
                #     统计用户截至到目前播放信息
                # --/
                region_list = list(redata.smembers("T_region_%s_%s"%(uid,date)))
                                
                for i in region_list:
                    LoadSum = redata.hget("T_regiontable_%s"%(date),"%s%s"%(uid,i))
                    uid_stat_t.update({"_id":uid},{"$inc":{
                                                    "Geo.%s.Load"%(i):int(LoadSum) 
                                                    }},upsert=True,w=0) 
                    uid_daily_t.update({"_id":date},{"$set":{
                                                    "Geo.%s.Load"%(i):int(LoadSum)
                                                    }},upsert=True,w=0) 
                                                                                    
                """获取用户截至到目前载入次数,播放次数,完成率之和"""
                uidnowstat = uid_stat_t.find_one({"_id":uid},{"_id":0,"Load":1,"Play":1,"EngageSum":1})
                uidnowload = int(uidnowstat["Load"])
                uidnowplay = int(uidnowstat["Play"])
                uidnowengagesum = float(uidnowstat["EngageSum"])
                
                
                """video nums for the uid up to now"""
                """average complete rate of total for the uid up to now"""
                """Calculate avarge click rate for the uid up to now"""
                
                uid_stat_t.update({"_id":uid},{"$set":{
                                                       "Nvideo":uidvideonums,
                                                       "Engage":operator.itruediv(uidnowengagesum,uidnowplay),
                                                       "Click":operator.itruediv(uidnowplay,uidnowload)
                                                       }})
                
                
                # --/ 
                #     统计用户类别播放信息
                # --/
                
                """获取该天有数据变动的类别名"""
                kidsdict = uid_type_t.find_one({"_id":date},{"_id":0})
                
                if kidsdict != None :
                
                    for kid in kidsdict:
                    
                        '''获取该类别视频数目'''
                    
                        sql = '''
                           SELECT a.vid FROM vinfo AS a
                           LEFT JOIN vsort AS b ON a.vsortid = b.id
                           WHERE b.kid= %s                           
                        '''
                        mysql_conn = MySQLdb.connect(host=self.mysqlIP,user=self.mysqlUser,passwd=self.mysqlPassword,port=self.mysqlPort,db=self.mysqlDbname,charset="utf8")
                                                                        
                        cursor = mysql_conn.cursor()  
                                                                          
                        param = (kid)
                                                                
                        n = cursor.execute(sql,param) 
                                    
                        kidvideonums = n
                                            
                        # --/
                        #     统计用户类别每天播放信息
                        # --/
                    
                        """获取用户该类别视频该天载入次数,播放次数"""
                        kiddailystat = uid_type_t.find_one({"_id":date},{"_id":0,kid:1})
                        kiddailyload = int(kiddailystat[kid]["Load"])
                        kiddailyplay = int(kiddailystat[kid]["Play"])
                    
                    
                        """video nums for the uid's kid daily"""
                        """Calculate avarge complete rate for the uid's kid daily"""
                        """Calculate avarge click rate for the uid's kid daily"""
                
                        uid_type_t.update({"_id":date},{"$set":{
                                                            "%s.Nvideo"%(kid):kidvideonums,
                                                            "%s.Engage"%(kid):operator.itruediv(float(redata.hget("T_engagesum_%s_%s"%(uid,date),kid)),kiddailyplay),
                                                            "%s.Click"%(kid):operator.itruediv(kiddailyplay,kiddailyload)
                                                            }})
                        
                        # --/
                        #     统计用户类别截至到目前播放信息
                        # --/
                    
                        """获取用户截至到目前载入次数,播放次数,完成率之和"""
                        #kidnowstat = uid_stat_t.find_one({"_id":kid},{"_id":0,"Load":1,"Play":1,"EngageSum":1})
                        #kidnowload = int(kidnowstat["Load"])
                        #kidnowplay = int(kidnowstat["Play"])
                        #kidnowengagesum = float(kidnowstat["EngageSum"])
                    
                        #"""video nums for the uid's kid up to now"""
                        #"""average complete rate of total for the uid's kid up to now"""
                        #"""average click rate of total for the uid's kid up to now"""
                    
                        #uid_stat_t.update({"_id":kid},{"$set":{
                        #                                   "Nvideo":kidvideonums,
                        #                                   "Engage":operator.itruediv(kidnowengagesum,kidnowplay),
                        #                                   "Click":operator.itruediv(kidnowplay,kidnowload)
                        #                                  }})
                                        
                request.end()
                
                '''--结束--'''   
                
                self.queue.task_done()
                                         
            except IOError,e:
                
                self.log.error("handleTUIDSET -- handle -- exception,%s"%(e))
               
                break



# --/
#     写数据去redis和mysql
# --/


class writeData(threading.Thread):
    
    def __init__(self,datadate,queue,mongoconn,redata,Config,logger):
        self.queue = queue
        self.redata = redata
        self.date = datadate
        
        self.mongoconn = mongoconn
        self.mysqlIP = Config.MysqldbIp        
        self.mysqlPort = Config.MysqldbPort
        self.mysqlUser = Config.MysqlUser
        self.mysqlPassword = Config.MysqlPassword
        self.mysqlDbname = Config.MysqlDbname
        self.Config = Config    
        
        self.logger = logger    
        
        """保存多少天的时间序列数据"""
        #self.daynums = 3650
        
        try:
            self.mysql_conn = MySQLdb.connect(host=self.mysqlIP,user=self.mysqlUser,passwd=self.mysqlPassword,port=self.mysqlPort,db=self.mysqlDbname,charset="utf8")
            self.cursor = self.mysql_conn.cursor()

        except Exception,e:
            print "can't connecte the mysql database."
            sys.exit()

        threading.Thread.__init__(self)
        
    def run(self):
        
        while True:
            
            """key format : T_engagesum_uid_date"""
            key = self.queue.get()
            
            uid = key.split("_")[2]
            
            item_list = redata.hkeys(key)
            
            for item in item_list:
                
                if len(item) == 7:
                    self.handleVid(uid,item)  
                elif len(item) == 4:
                    self.handleUid(item)
                elif len(item) == 6:
                    self.handleKid(uid,item)
            
            self.queue.task_done()
                            
    # --/
    #     更新redis中vid数据
    # --/                    
                                
    def handleVid(self,uid,vid): 
        
        uid_stat_t =  self.mongoconn["video"]["%s_stat"%(uid)]
        vid_play_t =  self.mongoconn["video"]["%s_play"%(vid)]
        uid_vdaily_t = self.mongoconn["video"]["%s_vdaily"%(uid)]
        
        """设置用户地域的载入次数"""
        
        """初始化vidinfo类"""
        vidinfObj = VidInfo(self.mysql_conn,self.mongoconn,vid)
        
        """得到该视频本天统计数据"""
        viddailydata =  uid_vdaily_t.find_one({"_id":self.date},{"_id":0,vid:1})
        
        Load = viddailydata[vid]["Load"]
        Play = viddailydata[vid]["Play"]
        IP = viddailydata[vid]["IP"]
        Engage = viddailydata[vid]["Engage"]
        Geo = viddailydata[vid]["Geo"]
        Click = viddailydata[vid]["Click"]
        Traffic = viddailydata[vid]["Traffic"]
        
        """计算地域分布数据中完成率"""
        for region in Geo:
            Geo[region]["Engage"] = operator.itruediv(float(Geo[region]["EngageSum"]), int(Geo[region]["ClickNum"]))
            
        """得到该视频实时播放最后100个记录"""
        plays_list = []
        plays_sum = vid_play_t.count()
        MaxSum = 100
        if plays_sum > MaxSum:
            plays_cursor = vid_play_t.find({"_id":{"$gt":(plays_sum-MaxSum)}})
        else:
            plays_cursor = vid_play_t.find().limit(MaxSum)

        for play in plays_cursor:
            vid_playtime = play["PlayTime"]
            redata.zadd("%s_SD7"%(vid),ujson.encode(play),vid_playtime)
    
        """得到该视频截至目前统计信息"""
        vidnowstat = vidinfObj.get_vid_info(vid)
        #vidnowstat = uid_stat_t.find_one({"_id":vid},{"_id":0,"EngageSum":0})
        vidnowstat.pop("HeatMapSum")
        
        nowGeo = vidnowstat["Geo"]
        nowHtmap = json.loads(vidnowstat["Htmap"])
        nowTraffic = vidnowstat["Traffic"]
        nowPlay = vidnowstat["Play"]
        nowClick = vidnowstat["Click"]
        nowPtmap = vidnowstat["Ptmap"]
        data = (nowPlay,nowClick,nowTraffic,vid)
        
        Htmp_min = min([k for i,j,k in nowHtmap])
        nowHtmap = [[i,j,k/Htmp_min] for i,j,k in nowHtmap ]

        """时间序列已存储多少天数据"""
        #days = redata.llen("%s_date"%(vid)) + 1
        
        """写数据到redis"""
        redpipe = self.redata.pipeline()
        redpipe.rpush("%s_date"%(vid), self.date)
        redpipe.rpush("%s_SD1"%(vid),Load)
        redpipe.rpush("%s_SD2"%(vid),Play)
        redpipe.rpush("%s_SD3"%(vid),IP)
        redpipe.rpush("%s_SD4"%(vid),Engage)
        redpipe.rpush("%s_SD5"%(vid),Click)
        redpipe.rpush("%s_SD6"%(vid),Traffic)
        redpipe.rpush("%s_SDD"%(vid),ujson.encode(Geo))
                
        redpipe.set("%s_PH"%(vid),ujson.encode(nowPtmap))
        redpipe.set("%s_SH"%(vid),ujson.encode(vidnowstat))
        redpipe.set("%s_SHH"%(vid),ujson.encode(nowGeo))
        redpipe.set("%s_JH"%(vid),ujson.encode(nowHtmap))
        
        """
        if days > self.daynums:
            redpipe.lpop("%s_date"%(vid))
            redpipe.lpop("%s_SD1"%(vid))
            redpipe.lpop("%s_SD2"%(vid))
            redpipe.lpop("%s_SD3"%(vid))
            redpipe.lpop("%s_SD4"%(vid))
            redpipe.lpop("%s_SD5"%(vid))
            redpipe.lpop("%s_SD6"%(vid))
            redpipe.lpop("%s_SDD"%(vid))
        """  
            
        redpipe.execute()
        
        
        sql = '''
            update  vinfo set playcount=%s,click_rate=%s,traffic=%s where vid = %s
        '''
                  
        self.cursor.execute(sql,data)              
        self.mysql_conn.commit()
        
        vidinfObj.update_vsum(vid,vidnowstat)
        vidinfObj.update_vgeo(vid,vidnowstat)
        vidinfObj.update_vhmap(vid,vidnowstat)
    
    # --/
    #     更新redis中uid数据
    # --/  


    def handleUid(self,uid):
        
        uid_stat_t =  self.mongoconn["video"]["%s_stat"%(uid)]
        uid_daily_t = self.mongoconn["video"]["%s_daily"%(uid)]
        
        #初始化uidinfo类
        uidinfObj = UidInfo(self.mysql_conn,self.mongoconn,uid)
        
        """得到该用户本天统计数据"""
        uiddailystat = uid_daily_t.find_one({"_id":self.date})
        
        Nvideo = uiddailystat["Nvideo"]
        Load = uiddailystat["Load"]
        Play = uiddailystat["Play"]
        IP = uiddailystat["IP"]
        Engage = uiddailystat["Engage"]
        Click = uiddailystat["Click"]
        Traffic = uiddailystat["Traffic"]
        Geo = uiddailystat["Geo"]
        
        """计算地域分布数据中完成率"""
        for region in Geo:
            Geo[region]["Engage"] = operator.itruediv(float(Geo[region]["EngageSum"]), int(Geo[region]["ClickNum"]))
        
        """得到该用户截至目前统计信息"""
        uidnowstat = uidinfObj.get_uid_info(uid)
        #uidnowstat = uid_stat_t.find_one({"_id":uid},{"_id":0,"EngageSum":0})
        
        nowGeo = uidnowstat["Geo"]
        nowTraffic = float(uidnowstat["Traffic"])
        nowMtraffic = float(uidnowstat["Mtraffic"])
        
        """时间序列已存储多少天数据"""
        #days = redata.llen("%s_date"%(uid)) + 1
        
        """写数据到redis"""
        redpipe = self.redata.pipeline()
        redpipe.rpush("%s_date"%(uid), self.date)
        redpipe.rpush("%s_UD1"%(uid),Nvideo)
        redpipe.rpush("%s_UD2"%(uid),Load)
        redpipe.rpush("%s_UD3"%(uid),Play)
        redpipe.rpush("%s_UD4"%(uid),IP)
        redpipe.rpush("%s_UD5"%(uid),Engage)
        redpipe.rpush("%s_UD6"%(uid),Click)
        redpipe.rpush("%s_UD7"%(uid),Traffic)
        redpipe.rpush("%s_UDD"%(uid),ujson.encode(Geo))
        
        redpipe.set("%s_UH"%(uid),ujson.encode(uidnowstat))
        redpipe.set("%s_UDH"%(uid),ujson.encode(nowGeo))        
        
        """
        if days > self.daynums:
            redpipe.lpop("%s_date"%(uid))
            redpipe.lpop("%s_UD1"%(uid))
            redpipe.lpop("%s_UD2"%(uid))
            redpipe.lpop("%s_UD3"%(uid))
            redpipe.lpop("%s_UD4"%(uid))
            redpipe.lpop("%s_UD5"%(uid))
            redpipe.lpop("%s_UD6"%(uid))
            redpipe.lpop("%s_UD7"%(uid))
            redpipe.lpop("%s_UDD"%(uid))
        """   
            
        redpipe.execute()
        
        uidinfObj.update_usum(uid,uidnowstat)
        uidinfObj.update_ugeo(uid,uidnowstat)
        
        playlist_info = uidinfObj.get_uid_playlist(uid)
        
        CreatXml(playlist_info,"adaptive")
        CreatXml(playlist_info,"video")
        
        filename1 = uid + "A0.xml"
        filename2 = uid + "A05.xml"
        Base_Hdfs_Path = "/static/" + uid + "/"
        HdfsObj = WebHadoop(self.Config.HdfsHost,self.Config.HdfsPort,self.Config.HdfsUser,self.logger,self.Config.HdfsPrefix)
        HdfsObj.put_file("/tmp/%s"%(filename1), Base_Hdfs_Path+filename1,overwrite="true")
        HdfsObj.put_file("/tmp/%s"%(filename2), Base_Hdfs_Path+filename2,overwrite="true")
        

    # --/
    #     更新redis中kid数据
    # --/  


    def handleKid(self,uid,kid):
        
        
        uid_stat_t =  self.mongoconn["video"]["%s_stat"%(uid)]
        uid_type_t = self.mongoconn["video"]["%s_type"%(uid)]
        
        # 初始化kidinfo 类
        kidinfObj = KidInfo(self.mysql_conn,self.mongoconn,kid)
        
        """得到用户本类本天统计数据"""
        kiddailydata =  uid_type_t.find_one({"_id":self.date},{"_id":0,kid:1})
    
        Nvideo = kiddailydata[kid]["Nvideo"]
        Load = kiddailydata[kid]["Load"]
        Play = kiddailydata[kid]["Play"]
        IP = kiddailydata[kid]["IP"]
        Engage = kiddailydata[kid]["Engage"]
        Click = kiddailydata[kid]["Click"]
        Traffic = kiddailydata[kid]["Traffic"]
        Geo = kiddailydata[kid]["Geo"]
        
        #获取kid对应的视频id的列表
        sql = '''
               SELECT a.vid FROM vinfo AS a
                LEFT JOIN vsort AS b ON a.vsortid = b.id
                WHERE b.kid= %s                           
            '''

        param = (kid)

        n = self.cursor.execute(sql,param)
        
        kidinfo = uid_stat_t.find_one({"_id":kid},{"_id":0})
        
        if kidinfo != None:
            uid_stat_t.remove({"_id":kid})
            print "kid removed"
        
        vidlist = self.cursor.fetchall()
        
        for i in vidlist:
            vid = i[0]
            vidtotalinfo = uid_stat_t.find_one({"_id":vid},{"_id":0})
            if vidtotalinfo != None : 
                uid_stat_t.update({"_id":kid},{"$inc":{
                                          "Click" : 0,
                                          "Engage" : 0,
                                          "EngageSum" : vidtotalinfo["EngageSum"],
                                          "IP": vidtotalinfo["IP"],
                                          "Load":vidtotalinfo["Load"], 
                                          "Play":vidtotalinfo["Play"],
                                          "Traffic":vidtotalinfo["Traffic"]
                                                   }},upsert=True,w=0)
                
                for geo in vidtotalinfo["Geo"].keys():
                    uid_stat_t.update({"_id":kid},{"$inc":{
                                          "Geo.%s.ClickNum"%geo : vidtotalinfo["Geo"][geo]["ClickNum"],
                                          "Geo.%s.EngageSum"%geo : vidtotalinfo["Geo"][geo]["EngageSum"],
                                          "Geo.%s.Load"%geo : vidtotalinfo["Geo"][geo]["Load"],
                                          "Geo.%s.Traffic"%geo : vidtotalinfo["Geo"][geo]["Traffic"]
                                                 }},upsert=True,w=0)
                    
        kidtotalnow = uid_stat_t.find_one({"_id":kid},{"_id":0})
        kidtotal_Load = kidtotalnow["Load"]
        kidtotal_Play = kidtotalnow["Play"]
        kidtotal_EngageSum = kidtotalnow["EngageSum"]
        uid_stat_t.update({"_id":kid},{"$set":{
                                          "Nvideo":n,
                                          "Click" : float(kidtotal_Play)/float(kidtotal_Load),
                                          "Engage": float(kidtotal_EngageSum)/int(kidtotal_Play)
                                                }},upset=True,w=0)
        
        print "kid geo update....."
        
        """计算地域分布数据中完成率"""
        for region in Geo:
            Geo[region]["Engage"] = operator.itruediv(float(Geo[region]["EngageSum"]), int(Geo[region]["ClickNum"]))
        
        """得到该用户截至目前统计信息"""
        kidnowstat = kidinfObj.get_kid_info(kid)
        
        nowGeo = kidnowstat["Geo"]
        nowTraffic = kidnowstat["Traffic"]
        nowPlay = kidnowstat["Play"]
        nowClick = kidnowstat["Click"]
        data = (nowPlay,nowClick,nowTraffic,kid) 
               
        """时间序列已存储多少天数据"""
        #days = redata.llen("%s_%s_date"%(uid,kid)) + 1
        
        """写数据到redis"""
        redpipe = self.redata.pipeline()
        redpipe.rpush("%s_date"%(kid), self.date)
        redpipe.rpush("%s_D1"%(kid),Nvideo)
        redpipe.rpush("%s_D2"%(kid),Load)
        redpipe.rpush("%s_D3"%(kid),Play)
        redpipe.rpush("%s_D4"%(kid),IP)
        redpipe.rpush("%s_D5"%(kid),Engage)
        redpipe.rpush("%s_D6"%(kid),Click)
        redpipe.rpush("%s_D7"%(kid),Traffic)
        redpipe.rpush("%s_DD"%(kid),ujson.encode(Geo))
        
        redpipe.set("%s_H"%(kid),ujson.encode(kidnowstat))
        redpipe.set("%s_DH"%(kid),ujson.encode(nowGeo))                

        """
        if days > self.daynums:
            redpipe.lpop("%s_%s_date"%(uid,kid))
            redpipe.lpop("%s_%s_D1"%(uid,kid))
            redpipe.lpop("%s_%s_D2"%(uid,kid))
            redpipe.lpop("%s_%s_D3"%(uid,kid))
            redpipe.lpop("%s_%s_D4"%(uid,kid))
            redpipe.lpop("%s_%s_D5"%(uid,kid))
            redpipe.lpop("%s_%s_D6"%(uid,kid))
            redpipe.lpop("%s_%s_D7"%(uid,kid))
            redpipe.lpop("%s_%s_DD"%(uid,kid))
        """   
            
        redpipe.execute()
        
        sql = '''
                update vsort set playcount=%s,click_rate=%s,traffic=%s where kid=%s
            '''
                
        self.cursor.execute(sql,data)         
        self.mysql_conn.commit()
        
        kidinfObj.update_ksum(kid,kidnowstat)
        kidinfObj.update_kgeo(kid,kidnowstat)
        
        print "kid mysql update successful!!"
 
 
def indent( elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i
    return elem

        
def CreatXml(info,type,player_url="http://www.skygrande.com/player/",video_url="http://video.skygrande.com/"):
    ''' create defalut playlist xml. like this:
     <?xml version='1.0' encoding='utf8'?>
     <rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:sgplayer="http://www.skygrande.com/player/">
       <channel>
         <title>MRSS Playlist Playlist</title>
         <item>
           <title>&lt;钱的化身&gt;预告片</title>
           <media:content url="http://video.skygrande.com/video/static/l123/l123TAl/play.m3u8" />
           <media:thumbnail url="http://video.skygrande.com/video/static/l123/l123TAl/play.jpg" />
           <description />
           <sgplayer:duration>01:25</sgplayer:duration>
           <sgplayer:provider>adaptive</sgplayer:provider>
         </item>
       </channel>
     </rss>     
     '''
    
    root = ET.Element('rss')

    
    root.set('version','2.0')
    root.set("xmlns:media","http://search.yahoo.com/mrss/")
    root.set("xmlns:sgplayer",player_url)
    channel = ET.SubElement(root,'channel')
    
    title = ET.SubElement(channel,"title")
    title.text = "MRSS Playlist Playlist" 
    
    for i in info:
        vid = i[1]
        uid = vid[0:4]
        videoname = i[2]
        base_path = video_url + "video/static/" + uid + "/" + vid
        filepath =  base_path + "/play.m3u8"
        if i[4] == 2:
            filepic =  base_path + "/preview." + i[5]
        else:
            filepic = base_path + "/play.jpg"
            
        duration = i[6]
        description = i[7]
        
        item_root = ET.SubElement(channel,"item")
        item_title = ET.SubElement(item_root,"title")
        item_title.text = videoname
        
        item_mediaconntent = ET.SubElement(item_root,"media:content")
        item_mediaconntent.set("url",filepath)                
        
        item_mediathum = ET.SubElement(item_root,"media:thumbnail")
        item_mediathum.set("url",filepic)
        
        item_desc = ET.SubElement(item_root,"description")
        item_desc.text =  description
        
        item_sgp_dura = ET.SubElement(item_root,"sgplayer:duration")
        item_sgp_dura.text =  duration
        
        item_sgp_pro = ET.SubElement(item_root,"sgplayer:provider")
        item_sgp_pro.text = type                             
      
    abc = indent(root)
    tree = ET.ElementTree(abc)
    if type == "adaptive":
        tree.write("/tmp/%sA0.xml"%uid,"utf8")  
        
    elif type == "video":
        tree.write("/tmp/%sA05.xml"%uid,"utf8")
    else:
        print "the type do not in platform list"



##############################

if __name__ == "__main__":
    
    try:
    
        logger = getLog("BatchPro",loglevel="debug")
         
        Database_Config = HandleConfig()
        
        #datadate = datetime.datetime.now().strftime("%Y%m%d")
        datadate = (datetime.datetime.now()+datetime.timedelta(days=1)).strftime("%Y%m%d")
        
        mongoconn = MongoClient(Database_Config.MongodbIp,27017)
        
         
        redispool = redis.ConnectionPool(host=Database_Config.RedisIp,port=6379,db=0)
        redata = redis.Redis(connection_pool=redispool)
        redpipe = redata.pipeline() 
        
        redata.rpush("date",datadate)
        
        workers = 10
        
        if isExists(logger,redpipe):
            
            for bvalue in redata.transaction(handleInit,"loadtable","playtable","endlist","regiontable"):
                if bvalue == False:
                    logger.error("Rename keys(loadtable,playtable,endlist,regiontable) fail")
                    sys.exit()
                    
            """添加当天日期到uid_rdate"""
            queue = Queue.Queue(0)
            for i in range(workers):
                worker_obj = HandleUserinfo(queue,logger,datadate,Database_Config)
                worker_obj.setDaemon(True) 
                worker_obj.start()
           
            user_list = list(redata.smembers("user_info"))
            for item in user_list:
                queue.put(item)
                
            queue.join()
            time.sleep(5)
            
            """处理T_endlist_$date队列"""
            queue = Queue.Queue(0)
            
            for i in range(workers):
                worker_obj = handleEndList(queue,logger,datadate,Database_Config)
                worker_obj.setDaemon(True)
                worker_obj.start()
            
            endlist_date = redata.lrange("T_endlist_%s"%(datadate),0,-1)
            endlist_list = list(set(endlist_date))
            for item in endlist_list:
                queue.put(item)
            
            queue.join()
            time.sleep(10)
            
            """处理T_VIDS_$date队列"""
            queue = Queue.Queue(0)
            
            for i in range(workers):
                worker_obj = handleTVIDSET(queue,logger,datadate,Database_Config)
                worker_obj.setDaemon(True)
                worker_obj.start()
            
            for item in redata.smembers("T_VIDS_%s"%(datadate)):
                queue.put(item)
            
            queue.join()
            time.sleep(10)
            
            """处理T_UIDS_$date队列"""
            queue = Queue.Queue(0)
            
            for i in range(workers):
                worker_obj = handleTUIDSET(queue,logger,datadate,Database_Config)
                worker_obj.setDaemon(True)
                worker_obj.start()
            
            for item in redata.smembers("T_UIDS_%s"%(datadate)):
                queue.put(item)
            
            queue.join()
            time.sleep(10)
            
        else:
                        
            logger.error("Does not satisfy the data processing requirements")
            sys.exit()
           
           
        """写数据去redis和mysql"""
        queue = Queue.Queue(0)
        
        for i in range(workers):
            worker_obj = writeData(datadate,queue,mongoconn,redata,Database_Config,logger)
            worker_obj.setDaemon(True)
            worker_obj.start()
        
        for item in redata.keys("T_engagesum_*_%s"%(datadate)):
            queue.put(item)
        
        queue.join()
            
        """删除临时数据"""
        delTmpData(redata)
                
    except IOError,e:
        
        logger.error(e)
        
    
         
