#!/usr/bin/env python
# -*- encoding:utf-8 -*-

'''
Created on Nov 23, 2012

@author: wye

Copyright @ 2011 - 2012  Cloudiya Tech . Inc 
'''

import re
import os
import sys
import json
import time
import redis
import pickle
import random
import socket
import logging
import MySQLdb
import operator
import subprocess
import pycurl
import StringIO
import threading
from decimal import *

#######################################

class execCmd():
    
    """ Execute command """
    
    def __init__(self,cmd,logger,killsig=-1,killtime=0):
        
        """
        killsig , default is unset
        killtime, default is unset 
        """
        self.cmd = cmd
        self.log = logger
        self.killsig = killsig
        self.killtime = killtime
        self.exception = None
        self.exit = None
        self.stdout = None
        self.stderr = None
        self.status = None
    
    def exeCmd(self):
        
        self.log.debug("Start run cmd : %s "%self.cmd)
        
        cmdobj = subprocess.Popen(self.cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        
        done = False
        while not done and self.killtime > 0:
            time.sleep(0.2)
            if cmdobj.poll():
                done = True
            self.killtime -=0.2
        
        if not done and self.killsig != -1:
            try:
                os.kill(cmdobj.pid, self.killsig)
            except OSError,e:
                self.log.error("Kill cmd fail : %s "%self.cmd)
                self.exception = e
        
        status = cmdobj.wait()
        self.status = status
        
        if os.WIFSIGNALED(status):
            self.exit = "SIGNAL: " + str(os.WTERMSIG(status))
        elif os.WIFEXITED(status):
            self.exit = str(os.WEXITSTATUS(status))
        else:
            self.exit = "UNKNOWN"
        
        self.stderr = cmdobj.stderr.read()
        self.stdout = cmdobj.stdout.readlines()
        
        cmdobj.stderr.close()
        
        self.log.debug("Cmd run end : %s "%self.cmd)
        
#######################################
class interWithMysql():
    
    def __init__(self,logger,vid):
        self.mysqlserver = "10.2.10.12"
        self.mysqluser = "cloudiya"
        self.mysqlpwd = "c10udiya"
        self.port = 3306
        
        self.logger = logger
        self.vid = vid
        

    def writeStatus(self,flag,iswmark,isrewrite,info=None):
        # --/
        #     视频状态对应关系（字段：status）
        #    （1）在上传视频进行处理与上传视频且打水印处理相关
        #     12 : 视频处理失败  
        #     22 : 视频处理成功
        #----------------------------------
        #    （2）对已通过审核的视频打水印 
        #     33 : 水印处理中（前端写？）
        #     34 : 水印处理失败
        #     23 : 水印处理成功
        #----------------------------------     
        # --/
        #     水印状态对应关系(字段:water)
        #      0 :  无水印 
        #      1 :  有水印 （如果用户选择打水印,在视频状态为22和23时将其置1）
        # --/
        
        if flag == "success":
            if iswmark and isrewrite:
                status = 23
            if iswmark and not isrewrite:
                status = 22
            if not iswmark and not isrewrite:
                status = 22
        if flag == "fail":
            if iswmark and isrewrite:
                status = 34
            if iswmark and not isrewrite:
                status = 12
            if not iswmark and not isrewrite:
                status = 12
                        
        try:
            dbconn = MySQLdb.connect(host=self.mysqlserver,user=self.mysqluser,passwd=self.mysqlpwd)
            dbcursor = dbconn.cursor()
            dbconn.select_db('video1')
            
            if int(status) == 22:
                if iswmark:
                    #有打水印
                    dbcursor.execute('update video set status=%s, water=%s where vid=%s',(status,1,self.vid))
                    self.logger.info("Congratulation,video and watermark handle success!!!,info : %s"%info)
                else:
                    #没打水印
                    dbcursor.execute('update video set status=%s where vid=%s',(status,self.vid))
                    self.logger.info("update video set status=%s where vid=%s"%(status,self.vid))
                    self.logger.info("Congratulation,video handle success!!!,info : %s"%info)
            
            elif int(status) == 23:
                #此种情况肯定是打了水印的
                dbcursor.execute('update video set status=%s, water=%s where vid=%s',(status,1,self.vid))
                self.logger.info("Congratulation,video and rewatermark handle success!!!,info : %s"%info)
                
            elif int(status) == 12:
                dbcursor.execute('update video set status=%s where vid=%s',(status,self.vid))
                if iswmark:
                    #有打水印
                    self.logger.info("Sorry,video and watermark handle fail!!!,Error info:%s"%info)
                else:
                    #没打水印
                    self.logger.info("Sorry,video handle fail!!!,Error info:%s"%info)
            elif int(status) == 34:
                #此种情况肯定是打了水印的
                dbcursor.execute('update video set status=%s where vid=%s',(status,self.vid))
                self.logger.info("Sorry,video and rewatermark handle fail!!!,Error info:%s"%info)
                
            dbconn.commit()                          
        except Exception,e:
            self.logger.error("update video status fail !!!!,error info : %s"%e)
            sys.exit()   
                
                
                     
    def writeBitRate(self,bitratelist):
        try:
            dbconn = MySQLdb.connect(host=self.mysqlserver,user=self.mysqluser,passwd=self.mysqlpwd)
            dbcursor = dbconn.cursor()
            dbconn.select_db('video1')
            for item in bitratelist:
                item.append(self.vid)
                dbcursor.execute('insert into vbitrate (level,flag,bitrate,vid) values(%s,%s,%s,%s)',item) 
            dbconn.commit()
        except Exception,e:
            self.logger.error("Write bitrate to mysql failure,error info : %s"%e)
            sys.exit()
     
     
    def writeVinfo(self,bitrate,vbitrate,abitrate,width,height,duration,size,format):
         ''' Write video base information to mysql ''' 
         
         size = float("%.1f"%operator.truediv(size,1024*1024))   
         
         '''Transform time format to 00:00:00'''
         duration = int(duration)
         
         minutes,seconds = "00","00"
        
         if duration/60 > 0:
             minutes = str(duration/60)
             seconds = str(duration%60)
         else:
             seconds = str(duration)
        
         time_format = ""
               
         for item in [minutes,seconds]:
             if len(item) == 1:
                 time_format = time_format+"0%s"%item+":"
             else:
                 time_format = time_format+item+":"
                         
         time_format = time_format.rstrip(":")    
         
         try:
            dbconn = MySQLdb.connect(host=self.mysqlserver,user=self.mysqluser,passwd=self.mysqlpwd)
            dbcursor = dbconn.cursor()
            dbconn.select_db('video1')
            params = (size,format,width,height,bitrate,vbitrate,abitrate,time_format,self.vid)
            dbcursor.execute('update video set size=%s,extension=%s,width=%s,height=%s,vcode_rate=%s,vcode_vrate=%s,vcode_arate=%s,duration=%s where vid=%s',params) 
            dbconn.commit()
         except Exception,e:
            self.logger.error("Write video base information to mysql failure,error info : %s"%e)
            sys.exit()        
    
    def getStatus(self):
        try:
            dbconn = MySQLdb.connect(host=self.mysqlserver,user=self.mysqluser,passwd=self.mysqlpwd)
            dbcursor = dbconn.cursor()
            dbconn.select_db('video1')
            sql = "select status from video where vid=%s"
            sql_result = dbcursor.execute(sql,(self.vid)) 
            status = dbcursor.fetchone()
            dbconn.commit()
        except Exception,e:
            self.logger.error("Failed to get file status: %s"%e)
            sys.exit()    
     
        return status[0] 

    def getPicStatus(self):
        try:
            dbconn = MySQLdb.connect(host=self.mysqlserver,user=self.mysqluser,passwd=self.mysqlpwd)
            dbcursor = dbconn.cursor()
            dbconn.select_db('video1')
            sql = "select preview from video where vid=%s"
            sql_result = dbcursor.execute(sql,(self.vid)) 
            status = dbcursor.fetchone()
            dbconn.commit()
        except Exception,e:
            self.logger.error("Failed to get preview picture status: %s"%e)
            sys.exit()    
     
        return status[0]
    
########################################

class interWithRedis():
    
    def __init__(self,logger,vid):
        
        self.RedisServer = "10.2.10.19"
        self.Port = 6379
        self.logger = logger
        self.vid = vid

    def WritetoRedis(self,key,value,db=0):
        try:
            redata = redis.Redis(host=self.RedisServer,port=self.Port,db=db)
            data = json.dumps(value)
            redata.set(key,data)

        except Exception,e:
            self.logger.error("Execute write bite into redis commands exception : %s"%e)
           
    def WriteUid_Date(self,key,value,db=0):
        redata = redis.Redis(host=self.RedisServer,port=self.Port,db=db)
        if not redata.exists(key):
            redata.lpush(key,value)     
        return True
    
    def WriteUid_set(self,key,value,db=0):
        redata = redis.Redis(host=self.RedisServer,port=self.Port,db=db)
        redata.sadd(key,value)
        return True
    
    def WriteUrlToCacheList(self,key,value,db=0):
        try:
            redata = redis.Redis(host=self.RedisServer,port=self.Port,db=db)
            redata.rpush(key,value)
        except Exception,e:
            self.logger.error("Write url to cdn cache list exception : %s"%e)
########################################

class runCmd():
    def __init__(self,logger,vid,iswatermark,isoverwrite):
        self.logger = logger
        self.vid = vid
        self.IsWaterMark = iswatermark
        self.IsOverWrite = isoverwrite
        self.stdout = None
        self.stdout = None
        self.status = None
        self.stderr = None
        self.exit = None
    
    def run(self,cmdlist,QuitFlag=True,Accelerate=False):
        if len(cmdlist) > 0:
            for cmd in cmdlist:
                CmdObj = execCmd(cmd,self.logger)
                CmdObj.exeCmd()
                self.status = CmdObj.status 
                self.stdout = CmdObj.stdout
                self.stderr = CmdObj.stderr
                self.exit = CmdObj.exit
                self.Write_Debug_Log(self.status,cmd,QuitFlag)

    def Only_One_Run(self,cmd,QuitFlag=False,Accelerate=False):
        CmdObj = execCmd(cmd,self.logger)
        CmdObj.exeCmd()
        self.status = CmdObj.status 
        self.stdout = CmdObj.stdout
        self.Write_Debug_Log(self.status,cmd,QuitFlag=False)


    def Write_Debug_Log(self,status,cmd,QuitFlag=True):
        MysqlObj = interWithMysql(self.logger,self.vid)
        if status != 0 and not QuitFlag:
            self.logger.error("Cmd : \"%s\" ,Exit code : %s"%(cmd,self.exit))
            self.logger.error("Cmd : \"%s\" ,Stderr : %s"%(cmd,self.stderr))
            self.logger.error("fetch a error ,but don't quit")
        if status != 0 and QuitFlag:
            self.logger.error("Cmd : \"%s\" ,Exit code : %s"%(cmd,self.exit))
            self.logger.error("Cmd : \"%s\" ,Stderr : %s"%(cmd,self.stderr))
            self.logger.error("Exec Cmd fail,quit!")
            MysqlObj.writeStatus("fail",self.IsWaterMark,self.IsOverWrite,info="Exec Cmd fail,quit!")
            sys.exit(self.status)  

########################################

def getlog(VideoFileNameAlias,logfile="/tmp/videohandle.log",loglevel="debug"):
    logger = logging.Logger(VideoFileNameAlias)
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter("%(asctime)s -- [ %(name)s ] -- %(levelname)s -- %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    if loglevel == "debug": 
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger

########################################

def getVideoMetaDList(linelist,flag):
    list = []
    for line in linelist:
        line = line.strip()
        if line == "[%s]"%flag:
            dict = {}
        elif line == "[/%s]"%flag:
            list.append(dict)
        else:
            try:
                key = line.split("=")[0]
                value = line.split("=")[1]
                dict[key]=value
            except IndexError:
                pass
    return list
    
#########################################

#########################################
# --/
#     GET KEY FRAME SPLIT POINTS
# --/
class getKFSplitPoint():
    
    def __init__(self,logger,ffprobe,videoname,videopath,VideoDuration,BlockSizeSecondNum,PartNums):
        self.videoname = videoname
        self.videopath = videopath
        self.VideoDuration = VideoDuration
        self.BlockSizeSecondNum = BlockSizeSecondNum
        self.PartNums = PartNums
        self.ffprobe = ffprobe
        self.logger = logger
        
    def getKFStdout(self,videoname,videopath):
        proc = subprocess.Popen("%s -show_frames %s"%(self.ffprobe,videopath),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        for line in iter(proc.stdout.readline,''):
            self.redata.rpush(videoname,line.rstrip())   

    def getKFTimeStamp(self):
        flag = "FRAME"
        KFrameFlag = False
        FrameBlockFlag = False
        KFTimeStampList = []
        try:
            tobj = threading.Thread(target=self.getKFStdout,args=(self.videoname,self.videopath))
            tobj.start()
            while True:
                lineobj = self.redata.blpop(self.videoname,10)
                if lineobj == None:
                    break
                else:
                    #HANDLE STDOUT LINE
                    line = lineobj[1].strip()
                    if line == "[%s]"%flag:
                        FrameBlockFlag = True
                    elif line == "[/%s]"%flag:
                        FrameBlockFlag = False
                    else:
                        try:
                            key = line.split("=")[0]
                            value = line.split("=")[1]
                            if key == "key_frame" and value == "1":
                                KFrameFlag = True
                            if KFrameFlag and FrameBlockFlag and key == "pkt_dts_time":
                                tlist = value.split(".")
                                newvalue = tlist[0] + "." + tlist[1][0:1]
                                TTime=Decimal(newvalue) - Decimal("0.1")
                                if TTime < 0:
                                    KFTimeStampList.append(Decimal(newvalue))
                                else:
                                    KFTimeStampList.append(TTime)
                                KFrameFlag = False
                        except Exception,e:
                            self.logger.error(e)
                            
            #LOG ALL KEY FRAME TIME STAMP
            TList = []
            for i in KFTimeStampList:
                TList.append("%s"%i)
            self.logger.debug("ALL KEY FRAME TIME STAMP : \n %s"%json.dumps(TList))
            
            return KFTimeStampList
        except Exception,e:
            self.logger.error(e)
            
    # --/
    #     ADD IN 20131107
    #     PARSE OUTPUT FORMAT IS CSV BY PYTHON
    # --/
    
    def getKFStdoutCSV(self,videoname,videopath):
        proc = subprocess.Popen("%s -show_frames -print_format csv %s"%(self.ffprobe,videopath),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        for line in iter(proc.stdout.readline,''):
            self.redata.rpush(videoname,line.rstrip())    

    def getKFTimeStampFromCSV(self):
        KFTimeStampList = []
        try:
            tobj = threading.Thread(target=self.getKFStdoutCSV,args=(self.videoname,self.videopath))
            tobj.start()
            while True:
                lineobj = self.redata.blpop(self.videoname,10)
                if lineobj == None:
                    break
                else:
                    itemlist = lineobj[1].split(",")
                    if itemlist[2] == "1":
                        value = itemlist[6]
                        tlist = value.split(".")
                        newvalue = tlist[0] + "." + tlist[1][0:1]
                        TTime=Decimal(newvalue) - Decimal("0.1")
                        if TTime < 0:
                            KFTimeStampList.append(Decimal(newvalue))
                        else:
                            KFTimeStampList.append(TTime)
            return KFTimeStampList
        except Exception,e:
            print(e)
            
    ##################################
    
    # --/
    #     ADD IN 20131107
    #     PARSE OUTPUT FORMAT IS CSV BY SHELL 
    # --/
    
    def getKFTimeStampFromCSVByShell(self):
        ShellScriptPath="/var/videohandle/mr/getKFListStr.sh"
        cmdobj=subprocess.Popen("/bin/bash %s %s %s"%(ShellScriptPath,self.ffprobe,self.videopath),shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        KFRawList=cmdobj.stdout.read().split(",")
        KFTimeStampList=[]
        for item in KFRawList:
            KFTimeStampList.append(Decimal(item))
        
        return KFTimeStampList
    ##################################
        
    def getSplitKFTStamp(self):
        TDict = {}
        #KFTimeStampList = self.getKFTimeStamp()
        #KFTimeStampList = self.getKFTimeStampFromCSV()
        KFTimeStampList = self.getKFTimeStampFromCSVByShell()
        for n in KFTimeStampList:
            for i in range(self.PartNums-1):
                if Decimal("%s"%(i*self.BlockSizeSecondNum)) < n <= Decimal("%s"%((i+1)*self.BlockSizeSecondNum)):
                    try:
                        prevalue = TDict["%s"%((i+1)*self.BlockSizeSecondNum)]
                        if n > prevalue:
                            TDict["%s"%((i+1)*self.BlockSizeSecondNum)] = n
                    except KeyError:
                        TDict["%s"%((i+1)*self.BlockSizeSecondNum)] = n
    
        SplitKFTStampList = ["0"]
        NTList = sorted(TDict.iteritems(),key=lambda e:int(e[0]))
        for item in NTList:
            SplitKFTStampList.append("%s"%item[1])
        
        SplitKFTStampList.append("%s"%self.VideoDuration)
        
        infostr = "VIDEO HAVE KEY FRAME,SPLIT INFORMATION"
        
        #IF NOT HAVE A KEY FRAME,THEN SPLIT IN THE ORIGINAL WAY
        if len(SplitKFTStampList) == 2:
            infostr = "VIDEO NO HAVE ANY KEY FRAME OR VIDEO HAVE KEY FRAME,BUT JUST ONLY ONE BLOCK,SPLIT INFORMATION"
            TList = ["0"]
            for i in range(self.PartNums-1):
                TList.append("%s"%((i+1)*self.BlockSizeSecondNum))       
            TList.append("%s"%self.VideoDuration)
            SplitKFTStampList = TList
        
        #LOG SPLIT POINT INFORMATION
        self.logger.info("%s : \n \
                          VideoDuration : %s \n \
                          Refer BlockSizeSecondNum : %s \n \
                          PartNums : %s \n \
                          SplitPointList: %s \n \
                         "%(infostr,self.VideoDuration,self.BlockSizeSecondNum,len(SplitKFTStampList)-1,json.dumps(SplitKFTStampList)))
        
        return SplitKFTStampList
    
    def main(self):
        self.logger.info("Start Calculation Video Split Time Point .... ")
        try:
            #import redis
            #redispool = redis.ConnectionPool(host="127.0.0.1",port=6379,db=0)
            #self.redata = redis.Redis(connection_pool=redispool)
            KFSplitPointList = self.getSplitKFTStamp()
            
            return "|".join(KFSplitPointList)
        except Exception,e:
            self.logger.error(e)
#########################################

######################################################################################
class hdfs():
    '''this is a class about hadoop command'''
    def __init__(self,logger,vid,hadoopbin,sourcePath=None,desPath=None):
        self.hadoopBin = hadoopbin
        self.rePath = sourcePath
        self.dePath = desPath
        self.exit = None
        self.stderr = None
        self.stdout = None
        self.status = None
        self.logger = logger
        self.vid = vid
        self.runObj = runCmd(self.logger,self.vid)
        
    def test_isdir(self,sourcePath):
        cmd = "%s fs -test -d %s" % (self.hadoopBin,sourcePath)
        self.runObj.Only_One_Run(cmd,QuitFlag=False,Accelerate=False)
        self.status = self.runObj.status
        return self.status
    
    def test_isfile(self,sourcePath):
        cmd = "%s fs -test -e %s" % (self.hadoopBin,sourcePath)
        self.runObj.Only_One_Run(cmd,QuitFlag=False,Accelerate=False)
        self.status = self.runObj.status
        return self.status  
          
    def mkdir(self,sourcePath):
        cmd = "%s fs -mkdir %s" % (self.hadoopBin,sourcePath)
        self.runObj.Only_One_Run(cmd,QuitFlag=False,Accelerate=False)
        self.status = self.runObj.status
        return self.status    
        
    def put(self,sourcePath,destinationPath):
        cmd = "%s fs -copyFromLocal %s %s" % (self.hadoopBin,sourcePath,destinationPath)
        self.runObj.Only_One_Run(cmd,QuitFlag=False,Accelerate=False)
        self.status = self.runObj.status
        return self.status  
                  
    def get(self,sourcePath,destinationPath):
        cmd = "%s fs -copyToLocal %s %s" % (self.hadoopBin,sourcePath,destinationPath)
        self.runObj.Only_One_Run(cmd,QuitFlag=False,Accelerate=False)
        self.status = self.runObj.status
        return self.status 
           
    def mv(self,sourcePath,destinationPath):
        cmd = "%s fs -mv %s %s" % (self.hadoopBin,sourcePath,destinationPath)
        self.runObj.Only_One_Run(cmd,QuitFlag=False,Accelerate=False)
        self.status = self.runObj.status
        return self.status    
 
    def cp(self,sourcePath,destinationPath):
        cmd = "%s fs -cp %s %s" % (self.hadoopBin,sourcePath,destinationPath)
        self.runObj.Only_One_Run(cmd,QuitFlag=False,Accelerate=False)
        self.status = self.runObj.status
        return self.status    
        
    def rmdir(self,sourcePath):
        cmd = "%s fs -rmr %s" % (self.hadoopBin,sourcePath)
        self.runObj.Only_One_Run(cmd,QuitFlag=False,Accelerate=False)
        self.status = self.runObj.status
        return self.status
    
    def ls(self,sourcePath):
        cmd = "%s fs -ls %s" % (self.hadoopBin,sourcePath)
        self.runObj.Only_One_Run(cmd,QuitFlag=False,Accelerate=False)
        self.status = self.runObj.status
        return self.status


########################################################################
# add the webhdfs class

class WebHadoop(object):
    '''
      WebHadoop 类是一个采用curl方式的hadoop集群的API接口
      初始话方式为：
       hdfs = WebHadoop("192.168.0.x","50071",username="yonghuming",loger)
       其中需要注意，在hadoop中需要开启hadoop的web接口。默认端口为50071.
       并且该机器能连接到后端的hadoop的datanode节点。因为在上传文件的时候需要访问后端节点。
       目前该类提供
       self.lsdir（）
       self.lsfile（）
       self.rename()
       self.remove()
       self.put_file()
       self.put_dir()
       self.checklink()
       self.mkdir()
      to do:
        self.append()

        AUTHOR :  LIRAN
        DATA : 2013-03-07
    '''
    def __init__(self,hosts,port,username,logger,prefix="/webhdfs/v1"):
        
        self.logger = logger
        self.host = self.GetHdfsGateway(hosts,port)
        self.port = port
        self.user = username
        self.prefix = prefix
        self.status = None
        self.url = "http://%s:%s" % (self.host,self.port)
        self.url_path = self.url + self.prefix 

    def GetHdfsGateway(self,hosts,port):
        
        #HDFS GATEWAY HA AND LB
        HostList = hosts.split(",")
        while True:
            if len(HostList) > 0:                 
                HostIndex = random.randint(0,len(HostList)-1)
                host = HostList[HostIndex]
                
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                try:
                    s.connect((host,int(port)))
                    s.settimeout(1)
                    return host
                    break
                except Exception,e:
                    self.logger.error("Don't connect to %s:%s , %s , retry other hdfs gateway"%(host,port,e))
                    HostList.remove(host)             
                finally:
                    s.close()
            else:
                self.logger.error("NO FIND ANY HDFS GATEWAY")
                sys.exit() 

    def checklink(self):
        b = StringIO.StringIO()
        c = pycurl.Curl()
        checkurl = self.url + "/dfsnodelist.jsp?whatNodes=LIVE"        
        try:

            c.setopt(pycurl.URL, checkurl)
            c.setopt(pycurl.HTTPHEADER, ["Accept:"])
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)
            c.perform()
            self.status = c.getinfo(c.HTTP_CODE)
            body = b.getvalue()
            self.Write_Debug_Log(self.status,checkurl)
            p = re.compile(r'''Live Datanodes :(.*)</a''')
            results = p.findall(body)
            b.close()
            if results[0] == "0":
                self.logger.error("Sorry, There are not live datanodes in Hadoop Cluster!!!")
                self.curlObj.close()
                sys.exit(255)
            return results[0]
        except pycurl.error,e:
            self.logger.error("Sorry, can not get the hadoop http link .Erros: %s" % e)
            c.close()
            b.close()
            sys.exit(255)
        finally:
            c.close()
            b.close()
            
    
    def lsdir(self,path):
        put_str = '[{"op":LISTSTATUS}]'
        lsdir_url = self.url_path + path + "?user.name=%s&op=LISTSTATUS"%self.user
        b = StringIO.StringIO()
        c = pycurl.Curl()
        try:
            c.setopt(pycurl.URL, lsdir_url)
            c.setopt(pycurl.HTTPHEADER, ["Accept:"])
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            body = b.getvalue()
            self.status = c.getinfo(pycurl.HTTP_CODE)
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
        
        if self.status == 200:
            data_dir = eval(body)
            return data_dir['FileStatuses']['FileStatus']
            
        else:
            self.logger.error("Sorry,can not list the dir or file status!!!")
            self.Write_Debug_Log(self.status,lsdir_url)
            return []
        
             
    def lsfile(self,path):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        put_str = '[{"op":LISTSTATUS}]'
        lsdir_url = self.url_path + path + "?user.name=%s&op=GETFILESTATUS"%self.user
        try:
            c.setopt(pycurl.URL, lsdir_url)
            c.setopt(pycurl.HTTPHEADER, ["Accept:"])
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            body = b.getvalue()
            self.status = c.getinfo(c.HTTP_CODE)
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
            
        if self.status == 200:
            data_dir = eval(body)
            if data_dir['FileStatus']['type'] == "DIRECTORY":
                self.logger.error("Sorry,this file %s is a dir actually!!!" % (path))
                return False
            else:
                return data_dir['FileStatus']
        else:
            self.logger.error("Sorry,can not list the dir or file status!!!")
            self.Write_Debug_Log(self.status,lsdir_url)
            return False
        
    def mkdir(self,path,permission="755"):
        b = StringIO.StringIO()
        c = pycurl.Curl()
        mkdir_str = '[{"op":"MKDIRS","permission"=permission}]'
        mkdir_url = "%s%s?user.name=%s&op=MKDIRS&permission=%s" % (self.url_path,path,self.user,permission)        
        try:

            c.setopt(pycurl.URL, mkdir_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(mkdir_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"PUT")
            c.setopt(pycurl.POSTFIELDS,mkdir_str)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.perform()
            self.status = c.getinfo(c.HTTP_CODE)
            body = b.getvalue()
            b.close()
        except Exception,e:
            print e
        finally:
            c.close()
            
         
        if self.status == 200 :
            if "true" in body:
                self.logger.info("Great,Successfully Create dir %s in hadoop cluster!!" % (path))
                return True
            elif "false" in body:
                self.logger.info("Sorry,can't create this %s dir in hadoop cluster!!1!!")
                return False
            else:
                return False
        else:
            self.logger.error("Sorry,can't create this %s dir in hadoop cluster!!1" % (path))
            self.Write_Debug_Log(self.status,mkdir_url) 
                    

    def remove(self,path,recursive="True"):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        remove_str = '''[{"op":"DELETE","recursive"="%s"}]''' % recursive
        remove_url = "%s%s?user.name=%s&op=DELETE&recursive=%s" % (self.url_path,path,self.user,recursive)        
        try:
            c.setopt(pycurl.URL, remove_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(remove_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"DELETE")
            c.setopt(pycurl.POSTFIELDS,remove_str)
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            body = b.getvalue()
            print body
            self.status = c.getinfo(c.HTTP_CODE) 
        except Exception,e:
            print "a"
            print e
        finally:
            c.close()
            b.close()
        if self.status == 200 :
            if "true" in body:
                self.logger.info("Great,Successfully delete dir or file %s in hadoop cluster!!" % (path))
                return True
            elif "false" in body:
                self.logger.info("Sorry,can't delete dir or file,maybe this dir is not exsited!!")
                return False
            else:
                return False
            
        else:
            self.logger.error("Sorry,can't create this %s dir in hadoop cluster!!1" % (path))
            self.Write_Debug_Log(self.status,remove_url)
            
    def rename(self,src,dst):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        rename_str = '[{"op":"RENAME"}]'
        rename_url = "%s%s?user.name=%s&op=RENAME&destination=%s" % (self.url_path,src,self.user,dst)        
        
        try:

            c.setopt(pycurl.URL, rename_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(rename_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"PUT")
            c.setopt(pycurl.POSTFIELDS,rename_str)
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            body = b.getvalue()
            self.status = c.getinfo(c.HTTP_CODE)  
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
        if self.status == 200 :
            if "true" in body:
                self.logger.info("Great,Successfully rename dir or file %s in hadoop cluster!!" % (rename_url))
                return True
            elif "false" in body:
                self.logger.info("Sorry,can't rename dir or file,maybe this dir is not exsited!!")
                return False
            else:
                return False
            
        else:
            self.logger.error("Sorry,can't create this %s dir in hadoop cluster!!1" % (rename_url))
            self.Write_Debug_Log(self.status,rename_url)     

    def put_file(self,local_path,hdfs_path,overwrite="false",permission="755",buffersize="64"):
        c = pycurl.Curl()
        put_url = "%s%s?user.name=%s&op=CREATE&overwrite=%s&permission=%s&buffersize=%s" % (self.url_path,hdfs_path,self.user,overwrite,permission,buffersize) 
               
        if os.path.isfile(local_path):
            try:
                f = file(local_path)
                filesize = os.path.getsize(local_path)
                c.setopt(pycurl.URL, put_url)
                c.setopt(pycurl.HTTPHEADER,['Content-Type:application/octet-stream','Transfer-Encoding:chunked'])
                c.setopt(pycurl.HEADER,1)
                c.setopt(pycurl.CUSTOMREQUEST,"PUT")
                c.setopt(pycurl.PUT,1)
                c.setopt(pycurl.INFILE,f)
                c.setopt(pycurl.INFILESIZE,filesize)
                b = StringIO.StringIO()
                c.setopt(pycurl.WRITEFUNCTION, b.write)
                c.setopt(pycurl.FOLLOWLOCATION, 1)
                c.setopt(pycurl.MAXREDIRS, 5)
                c.perform()
                print "yes.is ready to putting..."
                self.status = c.getinfo(c.HTTP_CODE)
                print b.getvalue()
            except Exception,e:
                print e
            finally:
                b.close()
                f.close()
        else:
            self.logger.error("Sorry,the %s is not existed,maybe it is not a file." % local_path)
            return False
        
        if self.status != 201:
            print self.status
            self.Write_Debug_Log(self.status,put_url)
            return False
        else:
            self.logger.info("Great,successfully put file into hdfs %s " % hdfs_path)
            return True


    def append(self,local_path,hdfs_path,buffersize=None):
        pass        
    
    def put_dir(self,local_dir,hdfs_path,overwrite="true",permission="755",buffersize="128"):
        dir_name = local_dir.split("/")[-1]
        if hdfs_path == "/":
            hdfs_path = hdfs_path + dir_name
            try:
                #self.mkdir(hdfs_path,permission):
                self.logger.info("Great,successful create %s hdfs_pash in hadoop." % hdfs_path)
            except Exception,e:
                print e
                self.logger.error("Sorry,create dir %s failure,errror" % hdfs_path)
                return False
            
        if os.path.isdir(local_dir):
            
            files = os.listdir(local_dir)
            print files
            for file in files:
                myfile = local_dir  + "/" + file
                put_file_path = hdfs_path + "/" + file
                if os.path.isfile(myfile):
                    self.put_file(myfile,put_file_path,overwrite,permission,buffersize)
                if os.path.isdir(myfile):
                    if self.mkdir(put_file_path,permission):
                        self.put_dir(myfile,put_file_path,overwrite,permission,buffersize)
                    else:
                        self.logger.error("Sorry,when putting dir to hadoop,can mkdir %s" % put_file_path)
                        return False
            return True
        else:
            self.logger.error("Sorry,local dir %s is not a directory." % local_dir)
            return False
        
    def get_file(self, local_path, hdfs_path,buffersize="128"):

        c = pycurl.Curl()
        f = file(local_path,'wb')
        get_str = '[{"op":"OPEN"}]'
        get_url = "%s%s?user.name=%s&op=OPEN&buffersize=%s" % (self.url_path,hdfs_path,self.user,buffersize)        
        try:

            c.setopt(pycurl.URL, get_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(get_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"GET")
            f = file(local_path,'wb')
            c.setopt(pycurl.POSTFIELDS,get_str)
            c.setopt(pycurl.WRITEFUNCTION,f.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,3600)
            c.setopt(pycurl.TIMEOUT,3600)            
            c.perform()
            self.status = c.getinfo(pycurl.HTTP_CODE)
            

        except Exception,e:
            print e
        finally:
            c.close()
            f.close()

        if self.status != 200:

            self.Write_Debug_Log(self.status,get_str)
            return False
        else:
            self.logger.info("Great,successfully get file from hdfs %s " % hdfs_path)
            return True
        
    def get_dir(self,local_dir,hdfs_dir,buffersize="128"):
        dir_list = self.lsdir(hdfs_dir)
        
        if not os.path.isdir(local_dir):
            os.mkdir(local_dir)
            
        if self.status != 200:
            self.logger.error("Sorry,the hdfs_dir %s is not exsited.." % hdfs_dir)
            return False
        
        for x,y in enumerate(dir_list):
            hdfs_path = hdfs_dir
            local_path = local_dir
            if y['type'] == "FILE":
                file_path = local_path + "/" + y['pathSuffix']
                hdfs_path = hdfs_path + "/" + y['pathSuffix']
                self.get_file(file_path,hdfs_path)
                if self.status == 200:
                    self.logger.info("Great,Successful get file %s from hadoop cluster" % hdfs_path)
                else:
                    self.logger.error("Sorry,can not get file from %s " % hdfs_path)
            elif y['type'] == "DIRECTORY":
                print "local_dir_path is %s" % local_path
                dir_path = local_path + "/" + y['pathSuffix']
                hdfs_path = hdfs_path + "/" + y['pathSuffix']
                if not os.path.isdir(dir_path):
                    os.mkdir(dir_path)
                try:
                    self.get_dir(dir_path,hdfs_path)
                except Exception,e:
                    print e
            else:
                pass
        
        return True
        
    def cat_file(self, hdfs_path,buffersize="128"):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        put_str = '[{"op":"OPEN"}]'
        put_url = "%s%s?user.name=%s&op=OPEN&buffersize=%s" % (self.url_path,hdfs_path,self.user,buffersize)        
        try:
            print "yes .ready to open"
            c.setopt(pycurl.URL, put_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(put_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"GET")
    
            c.setopt(pycurl.POSTFIELDS,put_str)
            c.setopt(pycurl.WRITEFUNCTION,b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            
            self.status = c.getinfo(pycurl.HTTP_CODE)
            print b.getvalue()
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
    
        if self.status != 200:
            self.Write_Debug_Log(self.status,put_str)
            return False
        else:
            self.logger.info("Great,successfully put file into hdfs %s " % hdfs_path)
            return True
    
    def copy_in_hdfs(self,src,dst,overwrite="true",permission="755",buffersize="128"):
        tmpfile = "/tmp/copy_inhdfs_tmpfile"
        self.get_file(tmpfile,src)
        if self.status == 200:
            self.put_file(tmpfile,dst,overwrite="true")
            if self.status == 201:
                os.remove(tmpfile)
                return True
            else:
                os.remove(tmpfile)
                return False
        else:
            os.remove(tmpfile)
            return False 
           
    def Write_Debug_Log(self,status,url):
        if status != 200 or status != 201 :
            self.logger.error("Url : \"%s\" ,Exit code : %s"%(url,self.status))
            self.logger.error("fetch a error ,but don't quit")

#####################################################################
#FOR HADOOP 1.0.3 

class WebHadoopOld(object):
    '''
      WebHadoop 类是一个采用curl方式的hadoop集群的API接口
      初始话方式为：
       hdfs = WebHadoop("192.168.0.x","50071",username="yonghuming",loger)
       其中需要注意，在hadoop中需要开启hadoop的web接口。默认端口为50071.
       并且该机器能连接到后端的hadoop的datanode节点。因为在上传文件的时候需要访问后端节点。
       目前该类提供
       self.lsdir（）
       self.lsfile（）
       self.rename()
       self.remove()
       self.put_file()
       self.put_dir()
       self.checklink()
       self.mkdir()
      to do:
        self.append()

        
        
        AUTHOR :  LIRAN
        DATA : 2013-03-07
    '''
    def __init__(self,host,port,username,logger,prefix="/webhdfs/v1"):
        self.host = host
        self.port = port
        self.user = username
        self.logger = logger
        self.prefix = prefix
        self.status = None
        self.url = "http://%s:%s" % (host,port)
        self.url_path = self.url + self.prefix 


    def checklink(self):
        b = StringIO.StringIO()
        c = pycurl.Curl()
        checkurl = self.url + "/dfsnodelist.jsp?whatNodes=LIVE"        
        try:

            c.setopt(pycurl.URL, checkurl)
            c.setopt(pycurl.HTTPHEADER, ["Accept:"])
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)
            c.perform()
            self.status = c.getinfo(c.HTTP_CODE)
            body = b.getvalue()
            self.Write_Debug_Log(self.status,checkurl)
            p = re.compile(r'''Live Datanodes :(.*)</a''')
            results = p.findall(body)
            b.close()
            if results[0] == "0":
                self.logger.error("Sorry, There are not live datanodes in Hadoop Cluster!!!")
                self.curlObj.close()
                sys.exit(255)
            return results[0]
        except pycurl.error,e:
            self.logger.error("Sorry, can not get the hadoop http link .Erros: %s" % e)
            c.close()
            b.close()
            sys.exit(255)
        finally:
            c.close()
            b.close()
            
    
    def lsdir(self,path):
        put_str = '[{"op":LISTSTATUS}]'
        lsdir_url = self.url_path + path + "?op=LISTSTATUS"
        b = StringIO.StringIO()
        c = pycurl.Curl()
        try:
            c.setopt(pycurl.URL, lsdir_url)
            c.setopt(pycurl.HTTPHEADER, ["Accept:"])
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            body = b.getvalue()
            self.status = c.getinfo(pycurl.HTTP_CODE)
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
            #pass
        
        if self.status == 200:
            data_dir = eval(body)
            return data_dir['FileStatuses']['FileStatus']
            
        else:
            self.logger.error("Sorry,can not list the dir or file status!!!")
            self.Write_Debug_Log(self.status,lsdir_url)
            return []
        
             
    def lsfile(self,path):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        put_str = '[{"op":LISTSTATUS}]'
        lsdir_url = self.url_path + path + "?op=GETFILESTATUS"
        try:
            c.setopt(pycurl.URL, lsdir_url)
            c.setopt(pycurl.HTTPHEADER, ["Accept:"])
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            body = b.getvalue()
            self.status = c.getinfo(c.HTTP_CODE)
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
            
        if self.status == 200:
            data_dir = eval(body)
            if data_dir['FileStatus']['type'] == "DIRECTORY":
                self.logger.error("Sorry,this file %s is a dir actually!!!" % (path))
                return False
            else:
                return data_dir['FileStatus']
        else:
            self.logger.error("Sorry,can not list the dir or file status!!!")
            self.Write_Debug_Log(self.status,lsdir_url)
            return False
        
    def mkdir(self,path,permission="755",num=0):
        b = StringIO.StringIO()
        c = pycurl.Curl()
        mkdir_str = '[{"op":"MKDIRS","permission"=permission}]'
        mkdir_url = "%s%s?op=MKDIRS&permission=%s" % (self.url_path,path,permission)        
        try:

            c.setopt(pycurl.URL, mkdir_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(mkdir_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"PUT")
            c.setopt(pycurl.POSTFIELDS,mkdir_str)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.perform()
            self.status = c.getinfo(c.HTTP_CODE)
            body = b.getvalue()
            b.close()
        except Exception,e:
            print e
        finally:
            c.close()
            
        if self.status == 200 :
            if "true" in body:
                self.logger.info("Great,Successfully Create dir %s in hadoop cluster!!" % (path))
                return True
            elif "false" in body:
                mkdirflag = "fail"
            else:
                mkdirflag = "fail"
        else:
            mkdirflag = "fail"
            
        if mkdirflag == "fail":
            if num < 1:
                self.logger.error("Sorry,can't create this %s dir in hadoop cluster,Again try mkdir" % (path))
                num = num + 1
                self.mkdir(path,permission="755",num=num)
            else:
                self.logger.error("Sorry,can't create this %s dir in hadoop cluster" % (path))
                self.Write_Debug_Log(self.status,mkdir_url)
                return False  
                    

    def remove(self,path,recursive="True"):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        remove_str = '[{"op":"DELETE","recursive"=recursive}]'
        remvoe_url = "%s%s?op=DELETE&recursive=%s" % (self.url_path,path,recursive)        
        try:

            c.setopt(pycurl.URL, remvoe_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(remove_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"DELETE")
            c.setopt(pycurl.POSTFIELDS,remove_str)
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            body = b.getvalue()
            self.status = c.getinfo(c.HTTP_CODE) 
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
        if self.status == 200 :
            if "true" in body:
                self.logger.info("Great,Successfully delete dir or file %s in hadoop cluster!!" % (path))
                return True
            elif "false" in body:
                self.logger.info("Sorry,can't delete dir or file,maybe this dir is not exsited!!")
                return False
            else:
                return False
            
        else:
            self.logger.error("Sorry,can't delete this %s dir in hadoop cluster!!1" % (path))
            self.Write_Debug_Log(self.status,remvoe_url)
            
    def rename(self,src,dst):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        rename_str = '[{"op":"RENAME"}]'
        rename_url = "%s%s?op=RENAME&destination=%s" % (self.url_path,src,dst)        
        try:

            c.setopt(pycurl.URL, rename_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(rename_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"PUT")
            c.setopt(pycurl.POSTFIELDS,rename_str)
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            body = b.getvalue()
            self.status = c.getinfo(c.HTTP_CODE)  
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
        if self.status == 200 :
            if "true" in body:
                self.logger.info("Great,Successfully rename dir or file %s in hadoop cluster!!" % (rename_url))
                return True
            elif "false" in body:
                self.logger.info("Sorry,can't rename dir or file,maybe this dir is not exsited!!")
                return False
            else:
                return False
            
        else:
            self.logger.error("Sorry,can't create this %s dir in hadoop cluster!!1" % (rename_url))
            self.Write_Debug_Log(self.status,rename_url)     

    def put_file(self,local_path,hdfs_path,overwrite="true",permission="755",buffersize="128",num=0):
        c = pycurl.Curl()
        put_str = '[{"op":"CREATE","overwrite":overwrite,"permission":permission,"buffersize":buffersize}]'
        put_url = "%s%s?op=CREATE&overwrite=%s&permission=%s&buffersize=%s" % (self.url_path,hdfs_path,overwrite,permission,buffersize)        
        try:

            c.setopt(pycurl.URL, put_url)
            header_str = StringIO.StringIO()
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(put_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"PUT")
            c.setopt(pycurl.HEADER,1)
            c.setopt(pycurl.HEADERFUNCTION,header_str.write)
            c.setopt(pycurl.POSTFIELDS,put_str)
            b = StringIO.StringIO()
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,3600)
            c.setopt(pycurl.TIMEOUT,3600)            
            c.perform()
            redirect_url = c.getinfo(pycurl.EFFECTIVE_URL)
            self.logger.info("local path is : %s , redirect_url is : %s"%(local_path,redirect_url))
        except Exception,e:
            self.logger.error("1 step put file %s fail : %s"%(local_path,e))
        
        if os.path.isfile(local_path):
            try:
                f = file(local_path)
                filesize = os.path.getsize(local_path)
                c.setopt(pycurl.URL, redirect_url)
                c.setopt(pycurl.HEADER,1)
                c.setopt(pycurl.CUSTOMREQUEST,"PUT")
                c.setopt(pycurl.PUT,1)
                c.setopt(pycurl.INFILE,f)
                c.setopt(pycurl.INFILESIZE,filesize)
                c.setopt(pycurl.WRITEFUNCTION, b.write)
                c.setopt(pycurl.FOLLOWLOCATION, 1)
                c.setopt(pycurl.MAXREDIRS, 5)
                c.perform()
                print "yes.is ready to putting..."
                self.status = c.getinfo(c.HTTP_CODE)
                print b.getvalue()
            except Exception,e:
                self.logger.error("2 step put file %s fail : %s"%(local_path,e))
            finally:
                b.close()
                header_str.close()
                f.close()
        else:
            self.logger.error("Sorry,the %s is not existed,maybe it is not a file." % local_path)
            return False
        

        if self.status != 201:
            print self.status
            if num < 1:
                num = num + 1
                self.logger.error("Sorry,put file %s fail,Again try put_file"%(local_path))
                self.put_file(local_path,hdfs_path,overwrite="true",permission="755",buffersize="128",num=num)
            else:
                self.logger.error("Sorry,put file %s fail"%(local_path))
                self.Write_Debug_Log(self.status,put_url)
                return False
        else:
            self.logger.info("Great,successfully put file into hdfs %s " % hdfs_path)
            return True

    def append(self,local_path,hdfs_path,buffersize=None):
        pass        
    
    def put_dir(self,local_dir,hdfs_path,overwrite="true",permission="755",buffersize="128"):
        dir_name = local_dir.split("/")[-1]
        if hdfs_path == "/":
            hdfs_path = hdfs_path + dir_name
            try:
                #self.mkdir(hdfs_path,permission):
                self.logger.info("Great,successful create %s hdfs_pash in hadoop." % hdfs_path)
            except Exception,e:
                print e
                self.logger.error("Sorry,create dir %s failure,errror" % hdfs_path)
                return False
            
        if os.path.isdir(local_dir):
            
            files = os.listdir(local_dir)
            print files
            for file in files:
                myfile = local_dir  + "/" + file
                put_file_path = hdfs_path + "/" + file
                if os.path.isfile(myfile):
                    self.put_file(myfile,put_file_path,overwrite,permission,buffersize)
                if os.path.isdir(myfile):
                    if self.mkdir(put_file_path,permission):
                        self.put_dir(myfile,put_file_path,overwrite,permission,buffersize)
                    else:
                        self.logger.error("Sorry,when putting dir to hadoop,can mkdir %s" % put_file_path)
                        return False
            return True
        else:
            self.logger.error("Sorry,local dir %s is not a directory." % local_dir)
            return False
        
    def get_file(self, local_path, hdfs_path,buffersize="128"):

        c = pycurl.Curl()
        f = file(local_path,'wb')
        get_str = '[{"op":"OPEN"}]'
        get_url = "%s%s?op=OPEN&buffersize=%s" % (self.url_path,hdfs_path,buffersize)        
        try:

            c.setopt(pycurl.URL, get_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(get_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"GET")
            f = file(local_path,'wb')
            c.setopt(pycurl.POSTFIELDS,get_str)
            c.setopt(pycurl.WRITEFUNCTION,f.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,3600)
            c.setopt(pycurl.TIMEOUT,3600)            
            c.perform()
            self.status = c.getinfo(pycurl.HTTP_CODE)
            

        except Exception,e:
            print e
        finally:
            c.close()
            f.close()

        if self.status != 200:

            self.Write_Debug_Log(self.status,get_str)
            return False
        else:
            self.logger.info("Great,successfully get file from hdfs %s " % hdfs_path)
            return True
        
    def get_dir(self,local_dir,hdfs_dir,buffersize="128"):
        dir_list = self.lsdir(hdfs_dir)
        
        if not os.path.isdir(local_dir):
            os.mkdir(local_dir)
            
        if self.status != 200:
            self.logger.error("Sorry,the hdfs_dir %s is not exsited.." % hdfs_dir)
            return False
        
        for x,y in enumerate(dir_list):
            hdfs_path = hdfs_dir
            local_path = local_dir
            if y['type'] == "FILE":
                file_path = local_path + "/" + y['pathSuffix']
                hdfs_path = hdfs_path + "/" + y['pathSuffix']
                self.get_file(file_path,hdfs_path)
                if self.status == 200:
                    self.logger.info("Great,Successful get file %s from hadoop cluster" % hdfs_path)
                else:
                    self.logger.error("Sorry,can not get file from %s " % hdfs_path)
            elif y['type'] == "DIRECTORY":
                print "local_dir_path is %s" % local_path
                dir_path = local_path + "/" + y['pathSuffix']
                hdfs_path = hdfs_path + "/" + y['pathSuffix']
                if not os.path.isdir(dir_path):
                    os.mkdir(dir_path)
                try:
                    self.get_dir(dir_path,hdfs_path)
                except Exception,e:
                    print e
            else:
                pass
        
        return True
        
    def cat_file(self, hdfs_path,buffersize="128"):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        put_str = '[{"op":"OPEN"}]'
        put_url = "%s%s?op=OPEN&buffersize=%s" % (self.url_path,hdfs_path,buffersize)        
        try:
            print "yes .ready to open"
            c.setopt(pycurl.URL, put_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(put_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"GET")
    
            c.setopt(pycurl.POSTFIELDS,put_str)
            c.setopt(pycurl.WRITEFUNCTION,b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            
            self.status = c.getinfo(pycurl.HTTP_CODE)
            print b.getvalue()
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
    
        if self.status != 200:
            self.Write_Debug_Log(self.status,put_str)
            return False
        else:
            self.logger.info("Great,successfully put file into hdfs %s " % hdfs_path)
            return True
    
    def copy_in_hdfs(self,src,dst,overwrite="true",permission="755",buffersize="128"):
        tmpfile = "/tmp/copy_inhdfs_tmpfile"
        self.get_file(tmpfile,src)
        if self.status == 200:
            self.put_file(tmpfile,dst,overwrite="true")
            if self.status == 201:
                os.remove(tmpfile)
                return True
            else:
                os.remove(tmpfile)
                return False
        else:
            os.remove(tmpfile)
            return False 
           
    def Write_Debug_Log(self,status,url):
        if status != 200 or status != 201 :
            self.logger.error("Url : \"%s\" ,Exit code : %s"%(url,self.status))
            self.logger.error("fetch a error ,but don't quit")

