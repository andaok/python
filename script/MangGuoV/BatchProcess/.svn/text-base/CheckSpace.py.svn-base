#!/usr/bin/env python
#-*- coding: utf-8 -*-

import time
import json
import datetime
import redis
import MySQLdb
#import Queue
#import threading
import sys
import logging
from pymongo import MongoClient
from pymongo import Connection
from UserInfo import UidInfo
from UserInfo import TypeInfo
import smtplib
from email.mime.text import MIMEText 
from PubMod import HandleConfig
from PubMod import getLog
from CheckFlow import Mail_list
from WebHdfsAPI import WebHadoop

from xml.etree import ElementTree as ET



subject = u"天空视频网：套餐将要到期"
text = u'''尊敬的天空视频网用户：

                    由于你购买的套餐或者充值空间已经到期，所以我们自动将您降级为免费用户，免费用户将有2GB/月的流量使用
                       和1GB的存储空间。如果您现在所有的视频文件所占用的存储空间超过1GB，我们将在7天后删除您的视频文件
                       到占用存储空间不超过1GB为止。

                    祝您使用愉快，如果您有什么建议或其他反馈请联系我们客服。

                    邮箱：support@skygrande.com.
               '''

B = []
def bag(S,n,Wlist,Vlist):
    #背包算法
    global B
      
    if S<0:
        return -1 # 不能装入更多的物品
    if S==0:     
        return 0 # 没有容量了
    if n<0:       # 没有物品
        return 0
        
    B0 = B[:]
    vBao = bag( S-Wlist[n] , n - 1,Wlist,Vlist )
    if vBao>=0:
        vBao = vBao + Vlist[n]
    B1 = B[:]
    B[:] = B0[:]
    vBuBao = bag( S , n - 1  ,Wlist, Vlist)
    if vBao>=vBuBao:
        B[:] = B1
        B[n] = 1
        return vBao
    else:
        B[n] = 0
        return vBuBao 
       
def CheckDate(today,startdate,enddate):
    #检测日期
    AheadNum = 7
    new_enddate = enddate + datetime.timedelta(days=8)
    new_startenddate = startdate + datetime.timedelta(days=8)
    new_startenddate_list = [ str( startdate + datetime.timedelta(days=i)).split()[0] for i in xrange(0,AheadNum)]
    AheadDay = [ str( enddate - datetime.timedelta(days=i)).split()[0] for i in xrange(0,AheadNum)]
    AfterDay = [ str( enddate + datetime.timedelta(days=i)).split()[0] for i in xrange(1,AheadNum+1)]
    DayList = AheadDay + AfterDay
    if today == str(enddate):
        return 0
    elif today in DayList :
        return 1
    elif today in new_startenddate_list:
        return 2
    elif today == str(new_startenddate) or today == str(new_enddate) :
        return 3
    else:
        return 4 
    
    
def getDelFiles(vidInfo,spaceNum):
    #背包算法：根据vid大小来确定要删除的文件，默认保留playcount最多的那几个视频文件。
    global B
    vid_list = [ i[0] for i in vidInfo ]
    vid_size_list = [ i[1]/1024 for i in vidInfo ]
    vid_playcount_list = [ i[2] for i in vidInfo ]
    remainfile_list = []
    delfile_list = []
    
    B = [ 0 for x in vid_list ]
    S = spaceNum
    N = len(vid_size_list)
    v = bag( S,N-1,vid_size_list,vid_playcount_list)    
    
    if 1 :
        #print "maxV=",v
        #print "B=",B 
        #print "W=",vid_size_list 
        #print "V=",vid_playcount_list
        #print "S=",S
        sw,sv="",""
        mw,mv=0,0
        for i in range(0,N):
            if B[i]==1:
                mw += vid_size_list[i]
                mv += vid_playcount_list[i]
                sw += "+ "+ str( vid_size_list[i] )+" "
                sv += "+ "+ str( vid_playcount_list[i] )+" "
                remainfile_list.append(vid_list[i])
        sw = "总重:"+ str( mw)+ "="+sw[1:]
        sv = "总价:"+ str( mv)+ "="+sv[1:]
        #print sw
        #print sv
        #print remainfile_list
        delfile_list = list(set(vid_list)-set(remainfile_list))
        print delfile_list
        return delfile_list
    else:
        return []

def delAll(Config,uidObj,redisconn,filelist,logger):
    #删除hadoop中的vid文件
    HdfsObj = WebHadoop(Config.HdfsHost,Config.HdfsPort,Config.HdfsUser,logger,Config.HdfsPrefix)
    uid = uidObj.Uid
    for i in filelist:
        uidObj.del_vid(i)
        i = i.encode('utf-8')
        path_inhdfs = "/static/%s/%s"%(uid,i)
        HdfsObj.remove(path_inhdfs)
        #HdfsObj.remove(file_sorcefile)
    
        
        
    playlist_list = uidObj.get_playinfo(uid)
    
    playlist_newlist = []
    
    for i in playlist_list:
        vid_inplaydir = json.loads(redisconn.get('%s_info'%i))
        vid_inplaylist = [ j for j in vid_inplaydir.itervalues()]
        print vid_inplaylist
        for k in  filelist:
            if vid_inplaylist and k in vid_inplaylist:
                playlist_newlist.append(i)
               
        
    updateXmlandRefresh(Config,uidObj,redisconn,HdfsObj,playlist_newlist)
    
def updateXmlandRefresh(Config,uidObj,redisconn,HdfsObj,playlist_newlist):
    #刷新upid的xml，默认播放列表不刷。有专门的步骤取刷新
    uid = uidObj.Uid

    for i in playlist_newlist:
        filename1 = i + ".xml"
        filename2 = i + "5.xml"
        filename3 = i + "A.xml" 

        upid_info = uidObj.get_upid_info(i)

        CreatXml(i,upid_info,"adaptive","PC")
        CreatXml(i,upid_info,"video","IOS")
        CreatXml(i,upid_info,"video","Android")

        Base_Hdfs_Path = "/static/" + uid + "/"                
        HdfsObj.put_file("/tmp/%s"%(filename1), Base_Hdfs_Path+filename1,overwrite="true")
        HdfsObj.put_file("/tmp/%s"%(filename2), Base_Hdfs_Path+filename2,overwrite="true")  
        HdfsObj.put_file("/tmp/%s"%(filename3), Base_Hdfs_Path+filename3,overwrite="true")
                                
        refresh_url1 = "/%s/%s.xml" % (uid,i)
        refresh_url2 = "/%s/%s5.xml" % (uid,i)
        refresh_url3 = "/%s/%sA.xml" % (uid,i)
                                
        redisconn.rpush("cacheurl_list",refresh_url1)
        redisconn.rpush("cacheurl_list",refresh_url2)
        redisconn.rpush("cacheurl_list",refresh_url3)            
    
    return True

def delFiles(config,uidObj,redisconn,freespace,vidused_info,totalspace,logger):
    #删除文件函数，首先获取要删除的文件列表，在对列表中文件批量删除。
    freeuser_space = freespace
    all_vidused_info = vidused_info
    total_userd_space = totalspace
    if freeuser_space >= total_userd_space:
        return True
    else:
        delFile_list = getDelFiles(all_vidused_info,freeuser_space)
    
    if delFile_list == []:
        return True
    else:
        print "delete begginning...."
        delAll(config,uidObj,redisconn,delFile_list,logger)
        
    
def SendAlarmMail(Mail_list,to,subject,text):
    #发送预警邮件
    msg = MIMEText(text,_charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = Mail_list["fromAddr"]
    msg["To"] = to
    try:
        send_smtp = smtplib.SMTP()
        send_smtp.connect(Mail_list["server"])
        send_smtp.sendmail(Mail_list["fromAddr"],to,msg.as_string())
        send_smtp.close()
        return True
    except Exception,e:
        print e
        pass    

def RenewSpace(uidobj,spaceinfo):
    uid = uidobj.Uid
    starttime = spaceinfo[0][1]
    endtime = spaceinfo[0][2]
    if endtime != None:
        AheadStarttime = starttime + datetime.timedelta(days=8)
    else:
        AheadStarttime = None
    months_count = spaceinfo[0][3]
    total_space = spaceinfo[0][4] 
       
    renewspaceinfo = uidobj.get_ext_spaceinfo(uid)
    if renewspaceinfo != []:
        renewspace_starttime = renewspaceinfo[0]
        renewspace_endtime = renewspaceinfo[1]
        renewspace_space = renewspaceinfo[2]
        renewmonth_count = renewspaceinfo[4]
        if endtime == renewspace_endtime :
            pass
        else:
            old_starttime_list = starttime.split("-")
            old_endtime_list = endtime.split('-')
            old_starttime_list[0] = str(old_endtime_list[0])
            new_starttime = '-'.join(old_starttime_list)
            new_enddate = renewspace_endtime
            new_month_count = renewmonth_count - month_count    
            uidobj.update_uspaceinfo(new_starttime,new_enddate,new_month_count,renewspace_space,uid)    
    
    
def CheckSpace(config,uidObj,mail_list,redisconn,today,logger):
    #检查空间，首先检测日期，如果本日-1天为结束日期，那么删除文件，如果为本日-8到本日-2天之间，那么发送邮件，否则不做任何动作
    uid = uidObj.Uid
    get_uidSpaceinfo = uidObj.get_uid_spaceinfo(uid)
    user_email = uidObj.get_user_email(uid)
    
    if get_uidSpaceinfo:
        starttime = get_uidSpaceinfo[0][1]
        endtime = get_uidSpaceinfo[0][2]
        if endtime != None:
            AheadStarttime = starttime + datetime.timedelta(days=8)
        else:
            AheadStarttime = None
        months_count = get_uidSpaceinfo[0][3]
        total_space = get_uidSpaceinfo[0][4]
    else:
        return False
    print "#################################3"
    print "uid is :",uid
    freeuser_space = uidObj.get_freeuser_space()
    all_vidused_info = uidObj.get_used_vidinfo(uidObj.Uid)
    total_userd_space = sum([i[1] for i in all_vidused_info])/1024  
      
    if endtime == None:
        Num = 2
    else:
        Num = CheckDate(today,starttime,endtime)  
    
    if Num == 0:
        RenewSpace(uidObj,get_uidSpaceinfo)
        SendAlarmMail(mail_list,user_email,subject,text)
    elif Num == 1:
        #user_email = 'rli@cloudiya.com'
        SendAlarmMail(mail_list,user_email,subject,text)
        #print "6"
    elif Num == 2:
        if total_userd_space >= total_space:
            #print "5"
            SendAlarmMail(mail_list,user_email,subject,text)
    elif Num == 3:
        delFiles(config,uidObj,redisconn,freeuser_space,all_vidused_info,total_userd_space,logger)
        return True
    else:
        return True 


def indent( elem, level=0):
    #格式化xml内容，使看起来整齐
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

        
def CreatXml(upid,info,provider,type,player_url="http://www.skygrande.com/player/",video_url="http://video.skygrande.com/"):
    #创建xml，格式如下
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
    
    uid = upid[0:4]
    for i in info:
        print "in create xml"
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
        tree.write("/tmp/%s.xml"%upid,"utf8") 
    elif type == "IOS":
        tree.write("/tmp/%s5.xml"%upid,"utf8")
    elif type == "Android":
        tree.write("/tmp/%sA.xml"%upid,"utf8")
    else:
        print "the type do not in platform list"



    

def main():
    #主函数入口
    Config = HandleConfig()
    today = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%Y-%m-%d") 
    redispool = redis.ConnectionPool(host=Config.RedisIp,port=6379,db=0)
    redata = redis.Redis(connection_pool=redispool)    
    mongoconn = MongoClient(Config.MongodbIp,27017)
    mysql_conn = MySQLdb.connect(host=Config.MysqldbIp,user=Config.MysqlUser,port=Config.MysqldbPort,passwd=Config.MysqlPassword,db=Config.MysqlDbname,charset="utf8")    

    logger = getLog("Step6",logfile=Config.LogFile,loglevel=Config.LogLevel)
    logger.info("Step6 Handle Start")

    set_alluser = redata.smembers("user_info")
    list_user = list(set_alluser)
    for i in list_user:
        uidObj = UidInfo(mysql_conn,mongoconn,i)
        CheckSpace(Config,uidObj,Mail_list,redata,today,logger)

    logger.info("Step6 Handle End")
        
if __name__ == "__main__":
    main()
