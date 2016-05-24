#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# -----------------------------------------/
#  GeTuiHttpApi Module 
#  @author: wye
#  @date: 2014-11-18
#  通过HTTP接口实现个推最基本模板和发送方式
#  @date: 2016-03-02
#  修改以支持家长，老师，园长三个APP的消息推送,先前只支持家长版消息推送 
#------------------------------------------/

import sys
import ujson
import redis
import logging
import threading
import logging.handlers

from igt_push import *
from igetui.template import *
from igetui.template.igt_base_template import *
from igetui.template.igt_transmission_template import *
from igetui.template.igt_link_template import *
from igetui.template.igt_notification_template import *
from igetui.template.igt_notypopload_template import *
from igetui.igt_message import *
from igetui.igt_target import *
from igetui.template import *

reload(sys)
sys.setdefaultencoding("utf-8")

class GeTui(threading.Thread):
    
    def __init__(self,NewsData):
        
        self.APPKEY = None
        self.APPID  = None
        self.MASTERSECRET = None
        self.HOST = "http://sdk.open.api.igexin.com/apiex.htm"
        self.logger = self.GetLog("GetuiApi")
        
        self.REDISIP = "10.2.10.19"
        self.REDISPORT = 6379
        self.REDISDB = 0
        self.NewsListName = "GetuiNewsList"
        
        self.TmpSaveNews = None
        self.NewsData = NewsData
        
        threading.Thread.__init__(self)
        
    def GetLog(self,logflag,loglevel="debug"):
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
    
    # ------------------------------------------ /
    # 推送模板
    # ------------------------------------------ /
    
    # -----/
    # 点击通知启动应用模板
    # -----/
    def NotificationTemplate(self,paradict):
        template = NotificationTemplate()
        
        template.appId = self.APPID
        template.appKey = self.APPKEY
        template.logo = "icon.png"    
        template.transmissionType = 1
        template.isRing = True
        template.isVibrate = True        
        template.isClearable = True       
        
        try:
            template.title = u"%s"%paradict["title"]
            template.text = u"%s"%paradict["text"]        
            #是否有透传内容
            if paradict.has_key("transmissionContent"):
                template.transmissionContent = u"%s"%paradict["transmissionContent"]
            else:
                template.transmissionContent = u"" 
            #是否指定logo路径
            if paradict.has_key("logoURL"):
                template.logoURL = paradict["logoURL"]
            else:
                template.logoURL = ""
        except KeyError:
            self.logger.error("NO find the key or key name error in news dict,discard the news and quit")
            sys.exit()
            
        return template  
        
    # ------/
    # 点击通知打开网页模板
    # ------/
    def LinkTemplate(self,paradict): 
        template = LinkTemplate()
        
        template.appId = self.APPID
        template.appKey = self.APPKEY
        template.logo = "icon.png"
        template.transmissionType = 1
        template.isRing = True
        template.isVibrate = True        
        template.isClearable = True
                     
        try:
            template.title = u"%s"%paradict["title"]
            template.text = u"%s"%paradict["text"]
            template.url = paradict["url"]
            #是否有透传信息，默认为空.
            if paradict.has_key("transmissionContent"):
                template.transmissionContent = u"%s"%paradict["transmissionContent"]
            else:
                template.transmissionContent = u''  
        except KeyError:
            self.logger.error("NO find the key or key name error in news dict,discard the news and quit")
            sys.exit()
                
        return template 


    # -------/
    # 通知栏弹框下载模板
    # -------/
    def NotyPopLoadTemplate(self,paradict):
        template = NotyPopLoadTemplate()
        template.appId = self.APPID
        template.appKey = self.APPKEY
        try:
            template.notyTitle = u"%s"%paradict["notyTitle"]   
            template.notyContent= u"%s"%paradict["notyContent"]
            
            template.notyIcon = "icon.png"
            template.logoUrl = ""        
            template.isRing = True
            template.isVibrate = True
            template.isClearable = True
            
            template.popTitle = u"%s"%paradict["popTitle"]
            template.popContent = u"%s"%paradict["popContent"]
            template.popImage = "icon.png"
            template.popButton1 = u"下载"
            template.popButton2 = u"取消"
        
            template.loadIcon = "icon.png"
            template.loadTitle = paradict["loadTitle"]
            template.loadUrl = paradict["loadUrl"]
            template.isAutoInstall = True
            template.isActive = False
        except KeyError:
            self.logger.error("NO find the key or key name error in news dict,discard the news and quit")
            sys.exit()
            
        return template
    
    # ------/
    # 透传消息模板
    # ------/
    def TransmissionTemplate(self,paradict):
        template = TransmissionTemplate()
        template.appId = self.APPID
        template.appKey = self.APPKEY
        template.transmissionType = 2
        
        #删除数据字典中style和temp字段
        del paradict["style"]
        del paradict["temp"]
        
        #获取以APNS方式发送消息时的消息体
        Apnsmess = u"%s"%paradict["title"] 
        
        #转换待发送消息体为字符串        
        MessStr = ujson.encode(paradict) 
        
        #个推接口发送透传消息
        template.transmissionContent = u"%s"%MessStr
        
        #APNS接口发送透传消息
        if paradict["type"] != "NotyLoad":
            template.setPushInfo("","",Apnsmess,"","","","","")
        
        return template
    
    # ------------------------------------------- /
    # 推送方式
    # ------------------------------------------- /
    
    # ------/
    # 对单个用户推送
    # ------/
    def pushMessageToSingle(self,paradict):
        push = IGeTui(self.HOST, self.APPKEY, self.MASTERSECRET)
        
        pushTemplate = paradict["temp"]
        if pushTemplate == "Notification":
            template = self.NotificationTemplate(paradict)
        elif pushTemplate == "Link":
            template = self.LinkTemplate(paradict)
        elif pushTemplate == "NotyPopLoad":
            template = self.NotyPopLoadTemplate(paradict)
        elif pushTemplate == "Transmission":
            template = self.TransmissionTemplate(paradict)
        else:
            self.logger.error("pushTemplate name error,discard the news and quit")
            sys.exit()
            
        message = IGtSingleMessage()
        message.isOffline = True
        message.offlineExpireTime = 1000 * 3600 * 12
        message.data = template
        
        try:
            cid = paradict["cid"]
        except KeyError:
            self.logger.error("NO find the key or key name error in news dict,discard the news and quit")
            sys.exit()           
             
        target = Target()
        target.appId = self.APPID
        target.clientId = cid
        ret = push.pushMessageToSingle(message,target)
        
        self.HandleRetVal(ret)
  
    # ------/
    # 对指定用户列表推送
    # ------/
    def pushMessageToList(self,paradict):
        push = IGeTui(self.HOST, self.APPKEY, self.MASTERSECRET)
        
        pushTemplate = paradict["temp"]
        if pushTemplate == "Notification":
            template = self.NotificationTemplate(paradict)
        elif pushTemplate == "Link":
            template = self.LinkTemplate(paradict)
        elif pushTemplate == "NotyPopLoad":
            template = self.NotyPopLoadTemplate(paradict)
        elif pushTemplate == "Transmission":
            template = self.TransmissionTemplate(paradict)
        else:
            self.logger.error("pushTemplate name error,discard the news and quit")
            sys.exit()
                        
        message = IGtListMessage()
        message.data = template
        message.isOffline = True
        message.offlineExpireTime = 1000 * 3600 * 12
                
        try:
            CidsStr = paradict["cid"]
        except KeyError:
            self.logger.error("NO find the key or key name error in news dict,discard the news and quit")
            sys.exit()                 
        
        targets = []
        CidsList = CidsStr.split(",")
        for cid in CidsList:
            target = Target()
            target.appId = self.APPID
            target.clientId = cid
            targets.append(target)
        
        contentId = push.getContentId(message)
        ret = push.pushMessageToList(contentId, targets)
        
        self.HandleRetVal(ret)
    
    # -------/
    # 对应用所有用户推送
    # -------/
    def pushMessageToApp(self,paradict):
        push = IGeTui(self.HOST, self.APPKEY, self.MASTERSECRET)

        pushTemplate = paradict["temp"]
        if pushTemplate == "Notification":
            template = self.NotificationTemplate(paradict)
        elif pushTemplate == "Link":
            template = self.LinkTemplate(paradict)
        elif pushTemplate == "NotyPopLoad":
            template = self.NotyPopLoadTemplate(paradict)
        elif pushTemplate == "Transmission":
            template = self.TransmissionTemplate(paradict)
        else:
            self.logger.error("pushTemplate name error,discard the news and quit")
            sys.exit()
            
        message = IGtAppMessage()
        message.data = template
        message.isOffline = True
        message.offlineExpireTime = 1000 * 3600 * 12
        message.appIdList.extend([self.APPID])
        ret = push.pushMessageToApp(message)
        
        self.HandleRetVal(ret)
    
    # ------/
    # 对返回结果进行处理
    # ------/        
    def HandleRetVal(self,RetValDict):
        self.logger.info("igetui server return info is : \n %s"%RetValDict)
        if RetValDict["result"] == "ok":
            self.logger.info("Push News success!!!")
        else:
            self.logger.error("Push News fail!!!,To re-write the News back to the list")
            RedisPool = redis.ConnectionPool(host=self.REDISIP,port=self.REDISPORT,db=self.REDISDB)
            Redata = redis.Redis(connection_pool=RedisPool)            
            Redata.rpush(self.NewsListName,self.TmpSaveNews)
    

    # ------/
    # 家长，老师，园长不同APP消息，载入不同APP个推认证信息.
    # ------/
    def LoadAppAuthInfo(self,NewsDict):
        if NewsDict.has_key("app") == False:
            self.APPKEY = "jYwfAMxU4U8wE900IgGy42"
            self.APPID  = "SEHaeuZDKqAqD9AaqRwFH4"
            self.MASTERSECRET = "aunBpzxXbdAyrE6iCRV0T"
        else:
            AppType = NewsDict["app"]
            if AppType == "jiazhang":
                self.APPKEY = "jYwfAMxU4U8wE900IgGy42"
                self.APPID  = "SEHaeuZDKqAqD9AaqRwFH4"
                self.MASTERSECRET = "aunBpzxXbdAyrE6iCRV0T"
            elif AppType == "yuanzhang":
                self.APPKEY = "HjdghFyw2H7Uu9w2ljwFB3"
                self.APPID  = "3R4Ndyjl7W7zhiOS33s5h3"
                self.MASTERSECRET = "ZMAOAc2Nib6bRFLxte0AO9"
            elif AppType == "laoshi":
                self.APPKEY = "lOhT8cYpM87p3YF19ls0e7"
                self.APPID  = "Q6FywF9EJEAnxcZgelZU13"
                self.MASTERSECRET = "LUKJ7ZU3PMA2CG4XYHZ6N1"
            else:
                self.logger.error("AppStyle name error,discard the news and quit")
                sys.exit()


    # ------/
    # 主函数
    # ------/
    def run(self):  
        self.logger.info("/**********************Start Push News************************/")
        self.logger.info("News Raw Data is : \n %s"%self.NewsData)
        if self.NewsData == None:
            self.logger.error("Message is none,quit")
            sys.exit()
        else:
            try:
                NewsDict = ujson.decode(self.NewsData)
            except Exception,e:
                self.logger.error("Parsing message error,quit")
                sys.exit()
            if NewsDict.has_key("type") == False or NewsDict.has_key("style") == False:
                self.logger.error("Send a message does not meet the conditions,discard the News and quit")
                sys.exit()
            else:
                self.LoadAppAuthInfo(NewsDict)
                self.TmpSaveNews = self.NewsData
                pushStyle = NewsDict["style"]
                if pushStyle == "pushMessageToSingle":
                    self.pushMessageToSingle(NewsDict)
                elif pushStyle == "pushMessageToApp":
                    self.pushMessageToApp(NewsDict)
                elif pushStyle == "pushMessageToList":
                    self.pushMessageToList(NewsDict)
                else:
                    self.logger.error("pushStyle name error,discard the news and quit")
                    sys.exit()
         
