#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# ------------------------------------------------ /
# Purpose:
#       Control camera script for start up ffmpeg process
#+      and monitor ffmpeg process 
# @author:wye
# @date:20141020
# @achieve basic functions
# ------------------------------------------------ /

import os
import sys
import time
import redis
import ujson
import logging
import MySQLdb
import datetime
import subprocess
import logging.handlers

def GetLog(logflag,loglevel="debug"):
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

class ffstart():
    
    def __init__(self,cid,logger):
        
        self.cid = cid
        self.logger = logger
        
        self.RedisServer = "10.2.10.19"
        self.RedisPort = 6379
        self.RedisDB = 0
                
        self.MysqlServer = "10.2.10.12"
        self.MysqlUser = "cloudiya"
        self.MysqlPasswd = "c10udiya"
        self.MysqlDB = "68baobao"       
        
        self.DataRootDir = "/Data"
        self.FFMPEG = "/usr/local/bin/ffmpeg"
                
        self.LivePlanRawData = None
        
        self.M3u8ModTime = None
        
        self.TimeStampNow = None
        self.date = None
        self.weekday = None
        
        self.unit_code = None
        self.router_addr = None
        self.router_port = None
        self.caiji_addr = None
        
    def GetCidLivePlan(self):
        try:
            RedisPool = redis.ConnectionPool(host=self.RedisServer,port=self.RedisPort,db=self.RedisDB)
            Redata = redis.Redis(connection_pool=RedisPool)
            LivePlanRawData = Redata.get("%s_live_minute"%self.cid)
            if LivePlanRawData == None:
                self.logger.error("No find related key in redis pool for %s live plan,Program quit"%self.cid)
                sys.exit()
            else:
                self.LivePlanRawData = LivePlanRawData
        except Exception,e:
            self.logger.error("Obtain %s live plan exception from redis pool,Error is %s,Program quit"%(self.cid,e))
            sys.exit()
    
    def GetCidBaseInfo(self):
        #  ---------------------------- /
        #  从MYSQL数据库获取和摄像头绑定的路由地址，路由端口和采集地址
        # ----------------------------- /
        try:
            DBConn = MySQLdb.connect(host=self.MysqlServer,user=self.MysqlUser,passwd=self.MysqlPasswd)
            DBCursor = DBConn.cursor()
            DBConn.select_db(self.MysqlDB)        
            SqlResultNum = DBCursor.execute('select unit_code,router_addr,router_port,caiji_addr,voice_state from t_device where index_code=%s',(self.cid))
            if SqlResultNum == 0 or SqlResultNum == None:
                self.logger.error("No find related record in t_device for cid %s,Program quit"%self.cid)
                sys.exit()
            else:            
                SqlResultVal = DBCursor.fetchone()
                DBConn.commit()
                self.unit_code = SqlResultVal[0]
                self.router_addr = SqlResultVal[1]
                self.router_port = SqlResultVal[2]
                self.caiji_addr = SqlResultVal[3]
                self.voice_state = int(SqlResultVal[4])
        except exception,e:
            self.logger.error("Obtain cid base info fail!!!")
            sys.exit()
        finally:
            DBConn.close()
            DBCursor.close()        
    
    def UpdateCidStatus(self):
        try:
            DBConn = MySQLdb.connect(host=self.MysqlServer,user=self.MysqlUser,passwd=self.MysqlPasswd)
            DBCursor = DBConn.cursor()
            DBConn.select_db(self.MysqlDB)          
            sql = 'update t_device set status=1 where index_code=%s'
            paras = (self.cid)
            DBCursor.execute(sql,paras)
            DBConn.commit()          
        except Exception,e:
            self.logger.error("Fatal Error,Connect to mysql exception for update cid status : %s,Error is : %s"%(self.cid,e))
            sys.exit()
        finally:
            DBConn.close()
            DBCursor.close()                    
    
    def IsExistFFmpeg(self):
        ptmp = subprocess.Popen("/bin/ps -aux | grep %s | grep -v grep | grep ffmpeg | wc -l"%self.cid,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        FFmpegNum = int(ptmp.stdout.read())
        if FFmpegNum == 1:
            return True
        else:
            return False
    
    def IsZeroPoint(self):
        PreDate = (datetime.datetime.strptime(self.date,"%Y%m%d") - datetime.timedelta(days=1)).strftime("%Y%m%d")
        YmdHMSTime_ZeroPointTime = PreDate + " " + "23:59:59"
        TimeStamp_ZeroPointTime = int(time.mktime(time.strptime(YmdHMSTime_ZeroPointTime, "%Y%m%d %H:%M:%S")))
        if 0 < self.TimeStampNow - TimeStamp_ZeroPointTime < 60:
            return True
        else:
            return False
            
    def IsInLiveTimeForHour(self):
        pass
                
    def IsInLiveTimeForMinute(self):
        TimeStampNow = self.TimeStampNow
        date = self.date
        weekday = self.weekday
        LivePlanDict = ujson.decode(self.LivePlanRawData)
        if LivePlanDict.has_key(weekday) == True:
            LivePlanWdayStr = LivePlanDict[weekday]
            LivePlanWdayList = LivePlanWdayStr.strip("{").strip("}").split(",")
            for live in LivePlanWdayList:
                LiveStartTime = live.split("-")[0]
                LiveEndTime = live.split("-")[1]
                #规范直播时段开始与结束时间
                LiveStartTime = LiveStartTime + ":00"
                LiveEndTime = LiveEndTime + ":00"
                if LiveEndTime == "24:00:00":LiveEndTime = "23:59:59"
                #获取直播时段开始与结束时间戳
                YmdHMSTime_LiveStartTime = date + " " + LiveStartTime
                YmdHMSTime_LiveEndTime = date + " " + LiveEndTime
                TimeStamp_LiveStartTime = int(time.mktime(time.strptime(YmdHMSTime_LiveStartTime, "%Y%m%d %H:%M:%S")))
                TimeStamp_LiveEndTime = int(time.mktime(time.strptime(YmdHMSTime_LiveEndTime, "%Y%m%d %H:%M:%S")))   
                if TimeStamp_LiveStartTime <= TimeStampNow <= TimeStamp_LiveEndTime:     
                    return True
            return False
        else:
            return False
    
    def IsM3u8Modify(self):
        CidDataRootDir = self.DataRootDir + "/" + self.unit_code + "/" + self.cid
        LiveM3u8Path = CidDataRootDir + "/" + "live.m3u8"
        
        if os.path.isfile(LiveM3u8Path) == True:
            cmd1str = "/bin/ls -l --time-style '+%s'"
            cmd2 = " %s | awk  '{print $6}'"
            cmd2str = cmd2%LiveM3u8Path
            cmdstr = cmd1str + cmd2str
            ptmp = subprocess.Popen(cmdstr,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                NewM3u8ModTime = int(ptmp.stdout.read())
                if self.M3u8ModTime != NewM3u8ModTime:
                    self.logger.info("M3u8 file have modify,Write value to m3u8modtime parameters")
                    self.M3u8ModTime = NewM3u8ModTime
                    return True
                else:
                    self.logger.info("M3u8 file no have modify")
                    return False
            except Exception,e:
                self.logger.error("Obtain M3u8ModTime value failure,program quit")
                sys.exit()
        else:
            self.logger.info("M3u8 file not exist")
            return False
                        
    def FFmpegRestart(self):
        self.FFmpegKill()
        self.FFmpegStart()
    
    def FFmpegStart(self):
        CidDataRootDir = self.DataRootDir + "/" + self.unit_code + "/" + self.cid
        LiveM3u8Path = CidDataRootDir + "/" + "live.m3u8"
        CidTsDir = CidDataRootDir + "/" + "media" + "/" + self.date
        url = self.caiji_addr.replace("ipaddr",self.router_addr)
        url = url.replace("port",str(self.router_port))
        YmdHMSTime_ZeroPointTime = self.date + " " + "00:00:00"
        TimeStamp_ZeroPointTime = int(time.mktime(time.strptime(YmdHMSTime_ZeroPointTime, "%Y%m%d %H:%M:%S")))
        SegStartNum = (self.TimeStampNow - TimeStamp_ZeroPointTime)/10 + 1
        
        # -------------- /
        # FFMPEG启动参数
        # -------------- /
        self.logger.info("FFmpeg all startup paracmeters list : \n \
                          CidDataRootDir : %s                   \n \
                          LiveM3u8Path : %s                     \n \
                          CidTsDir : %s                         \n \
                          url : %s                              \n \
                          SegStartNum : %s                      \n \
                        "%(CidDataRootDir,LiveM3u8Path,CidTsDir,url,SegStartNum))
                
        # -------------- /
        # FFMPEG在每日零点附近重启后创建本天TS存储目录
        # -------------- /
        if os.path.isdir(CidTsDir) == False:
            rcode = subprocess.call("/bin/mkdir -p %s"%CidTsDir,shell=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)
            if rcode == 0:
                self.logger.info("Create dir %s success!!!"%CidTsDir)
            else:
                self.logger.info("Create dir %s failure!!!"%CidTsDir)            
        
        # --------------- /
        # 启动FFMPEG进程
        # 0 -- 摄像头带拾音器,默认是0
        # 1 -- 摄像头不带拾音器
        # --------------- /
        if self.voice_state == 1:
            cmd="cd %s && %s -d -f rtsp -rtsp_transport tcp -i %s -f lavfi -i aevalsrc=\"0::s=8000\" -map 0:0 -map 1:0 -vcodec copy -acodec libfaac -b:a 2k -f segment -segment_time 10 -segment_list_size 2 -segment_list %s -segment_start_number %s -segment_list_type m3u8 -segment_format mpegts media/%s/%s" 
            cmdstr = cmd%(CidDataRootDir,"/usr/local/bin/ffmpeg.audio",url,LiveM3u8Path,SegStartNum,self.date,self.date)
            cmdstr = cmdstr + "%05d.ts > /dev/null &"
        else:
            cmd="%s -d -f rtsp -rtsp_transport tcp -i %s -vcodec copy -acodec libfaac -b:a 15k -map 0 -f segment -segment_time 10 -segment_list_size 2 -segment_list_entry_prefix media/%s/ -segment_list %s -segment_start_number %s -segment_list_type m3u8 -segment_format mpegts %s/%s" 
            cmdstr = cmd%(self.FFMPEG,url,self.date,LiveM3u8Path,SegStartNum,CidTsDir,self.date)
            cmdstr = cmdstr + "%05d.ts > /dev/null &"
 
        self.logger.info("StartUp FFmpeg Cmd : %s"%cmdstr)
        rcode = subprocess.call(cmdstr,shell=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)
        if rcode == 0:
            self.logger.info("FFmpeg process startup success!!!")
            if self.voice_state == 1:
                self.logger.info("Delete redundant process of startup ffmpeg for no voice camera")
                rcode = subprocess.call("/bin/ps -ef | grep ffmpeg | grep %s | grep cd |grep -v grep | awk '{print $2}' | xargs kill -9"%self.cid,shell=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)
                if rcode == 0:
                   self.logger.info("Kill redundant ffmpeg process success!!!")
                else:
                   self.logger.info("Kill redundant ffmpeg process failure!!!")
        else:
            self.logger.info("FFmpeg process startup failure!!!")     
            
        # ------------- /
        # 等待启动成功
        # ------------- /
        #time.sleep(30)
        
        # ------------- /
        # 更新摄像头状态
        # ------------- /
        #if self.IsExistFFmpeg() == True:
        #    self.UpdateCidStatus()
        
        # -------------- /
        # 写live.m3u8文件修改时间到特定参数
        # -------------- /
        if os.path.isfile(LiveM3u8Path) == True:
            cmd1str = "/bin/ls -l --time-style '+%s'"
            cmd2 = " %s | awk  '{print $6}'"
            cmd2str = cmd2%LiveM3u8Path
            cmdstr = cmd1str + cmd2str
            ptmp = subprocess.Popen(cmdstr,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)            
            try:
                NewM3u8ModTime = int(ptmp.stdout.read())
                self.M3u8ModTime = NewM3u8ModTime
            except Exception,e:
                self.logger.error("Obtain M3u8ModTime value failure,program quit,Error is %s"%e)
                sys.exit()

    def FFmpegKill(self):
        rcode = subprocess.call("/bin/ps -ef | grep ffmpeg | grep %s | grep -v grep | awk '{print $2}' | xargs kill -9"%self.cid,shell=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)
        if rcode == 0:
            self.logger.info("Kill ffmpeg process success!!!")
        else:
            self.logger.info("Kill ffmpeg process failure!!!")
        
    def ObjInit(self):
        self.GetCidLivePlan()
        self.GetCidBaseInfo()
        
    def main(self):
        while True:
            self.TimeStampNow = int(time.time())
            self.date = datetime.datetime.now().strftime("%Y%m%d")
            self.weekday = str(time.strptime(self.date,"%Y%m%d").tm_wday+1)
            if self.IsInLiveTimeForMinute() == True:
                if self.IsExistFFmpeg() == True:
                    if self.IsZeroPoint() == True:
                        self.logger.info("Restart ffmpeg process in zero point!!!")
                        self.FFmpegRestart()
                        time.sleep(30)
                        continue
                    if self.IsM3u8Modify() == False:
                        self.logger.info("Restart ffmpeg process for m3u8 file is not modify")
                        self.FFmpegRestart()
                else:
                    self.logger.info("Now is on live time segment,But don't find ffmpeg process,Start up it")
                    self.FFmpegStart()                
            else:
                if self.IsExistFFmpeg() == True:
                    self.logger.info("Now isn't on live time segment,But have ffmpeg process,kill it")
                    self.FFmpegKill()
                else:
                    self.logger.info("Now isn't on live time segment,Nothing do")                
                    
            time.sleep(30)
                             
if __name__ == "__main__":
    if len(sys.argv) == 2 and len(sys.argv[1]) == 8:
        cid = sys.argv[1]
        logger = GetLog(cid)
        FFstartObj = ffstart(cid,logger)
        FFstartObj.ObjInit()
        FFstartObj.UpdateCidStatus()
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError, e: 
            print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
            sys.exit(1)
        # decouple from parent environment
        os.chdir("/")
        os.setsid() 
        os.umask(0) 
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent, print eventual PID before
                #print "Daemon PID %d" % pid 
                sys.exit(0) 
        except OSError, e: 
            print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
            sys.exit(1) 
        # start the daemon main loop
        try:
            FFstartObj.main()
        except Exception,e:
            logger.error("Main Program Quit,Error is %s"%e)
            sys.exit()
    else:
        print "Parameter does not meet the requirements,Program quit"
        sys.exit()

