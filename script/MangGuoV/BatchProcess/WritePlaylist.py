#!/usr/bin/env python
#-*- coding: utf-8 -*-

import time
import json
import ujson
import datetime
import redis
import MySQLdb
import Queue
import threading
from pymongo import MongoClient
from UserInfo import UidInfo
from UserInfo import TypeInfo

from PubMod import HandleConfig
from PubMod import getLog
from WebHdfsAPI import WebHadoop
from xml.etree import ElementTree as ET

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

        
def CreatXml(uid,info,provider,type,player_url="http://www.skygrande.com/player/",video_url="http://video.skygrande.com/"):
    
    ''' create defalut playlist xml. like this:
     <?xml version='1.0' encoding='utf8'?>
     <rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:sgplayer="http://www.skygrande.com/player/">
       <channel>
         <title>MRSS Playlist Playlist</title>
         <item>
           <title>&lt;钱的化身&gt;预告片</title>
           <media:content url="http://video.skygrande.com/video/static/l123/l123TAl/play.m3u8" />
           <media:thumbnail url="http://video.skygrande.com/video/static/l122/l123TAl/play.jpg" />
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
        videoname = i[2]
        base_path = video_url + "video/static/" + uid + "/" + vid
        if type == "Android":
            filepath = base_path + "/play.mp4"
        else:
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
        item_sgp_pro.text = provider                             
      
    abc = indent(root)
    tree = ET.ElementTree(abc)
    if type == "PC":
        tree.write("/tmp/%sA0.xml"%uid,"utf8")  
    elif type == "IOS":
        tree.write("/tmp/%sA05.xml"%uid,"utf8")
    elif type == "Android":
        tree.write("/tmp/%sA0A.xml"%uid,"utf8")
    else:
        print "the type do not in platform list"


class WriteDefaultPlaylist(threading.Thread):
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
            
        try:
            self.mysql_conn = MySQLdb.connect(host=self.mysqlIP,user=self.mysqlUser,passwd=self.mysqlPassword,port=self.mysqlPort,db=self.mysqlDbname,charset="utf8")
            self.cursor = self.mysql_conn.cursor()

        except Exception,e:
            print "can't connecte the mysql database."
    
        threading.Thread.__init__(self)
    
    def run(self):
        while True:
                    
            uid = self.queue.get()
                    
            userObj = UidInfo(self.mysql_conn,self.mongoconn,uid)
            
            playlist_info = userObj.get_uid_playlist(uid)
                           
            CreatXml(uid,playlist_info,"adaptive","PC")
            CreatXml(uid,playlist_info,"video","IOS")
            CreatXml(uid,playlist_info,"video","Android")
            "写入默认播放列表"
            defaultplaylist = {}
            for i in xrange(0,len(playlist_info)):
                vid_inlist = playlist_info[i][1]
                defaultplaylist[str(i+1)] = vid_inlist
                self.redata.set("%sA0_info"%(uid),ujson.encode(defaultplaylist))
                           
            filename1 = uid + "A0.xml"
            filename2 = uid + "A05.xml"
            filename3 = uid + "A0A.xml"
            Base_Hdfs_Path = "/static/" + uid + "/"
            HdfsObj = WebHadoop(self.Config.HdfsHost,self.Config.HdfsPort,self.Config.HdfsUser,self.logger,self.Config.HdfsPrefix)
            HdfsObj.put_file("/tmp/%s"%(filename1), Base_Hdfs_Path+filename1,overwrite="true")
            HdfsObj.put_file("/tmp/%s"%(filename2), Base_Hdfs_Path+filename2,overwrite="true")  
            HdfsObj.put_file("/tmp/%s"%(filename3), Base_Hdfs_Path+filename3,overwrite="true")
                    
            refresh_url1 = "/%s/%sA0.xml" % (uid,uid)
            refresh_url2 = "/%s/%sA05.xml" % (uid,uid)
            refresh_url3 = "/%s/%sA0A.xml" % (uid,uid)
                    
            self.redata.rpush("cacheurl_list",refresh_url1)
            self.redata.rpush("cacheurl_list",refresh_url2)
            self.redata.rpush("cacheurl_list",refresh_url3)            
            
            self.queue.task_done()

def main():
    Config = HandleConfig()
    redispool = redis.ConnectionPool(host=Config.RedisIp,port=6379,db=0)
    redata = redis.Redis(connection_pool=redispool)    
    mongoconn = MongoClient(Config.MongodbIp,27017)
    
    
    logger = getLog("Step7",logfile=Config.LogFile,loglevel=Config.LogLevel)
    logger.info("Step7 Handle Start")
            
    datadate = Config.date    
    queue = Queue.Queue(0)
        
    list_user = list(redata.smembers("user_info")) 
          
    for i in range(Config.workers):
        worker_obj = WriteDefaultPlaylist(datadate,queue,mongoconn,redata,Config,logger)
        worker_obj.setDaemon(True)
        worker_obj.start()
            
    for item in list_user:
        print item
        queue.put(item)
            
    queue.join()
    logger.info("Step7 Handle End") 
    

if __name__ == "__main__":
    main()    

