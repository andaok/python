#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os
import sys
import time
import redis
import ujson
import random
import smtplib
import logging
import MySQLdb
import datetime
import threading
import subprocess
import ConfigParser
import logging.handlers
from WebHDFSApi import WebHadoop
from email.header import Header
from email.mime.text import MIMEText


# --------------------------------------- /
# 自定义异常类
# --------------------------------------- /
class CustomVodException(Exception):

    def __init__(self,flag,info):

        Exception.__init__(self)

        self.flag = flag

        self.info = info

# --------------------------------------- /
# 执行SHELL脚本核心模块
# --------------------------------------- /
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
    
    def exeCmd(self,StdoutFlag):
        
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
        if StdoutFlag == "read":
            self.stdout = cmdobj.stdout.read()
        else:
            self.stdout = cmdobj.stdout.readlines()
        
        cmdobj.stderr.close()
        
        self.log.debug("Cmd run end : %s "%self.cmd)

# ----------------------------------------- /
# 执行SHELL脚本中间模块
# ----------------------------------------- /
class runCmd():
    def __init__(self,logger):
        self.logger = logger
        self.stdout = None
        self.stdout = None
        self.status = None
        self.stderr = None
        self.exit = None
    
    def run(self,cmdlist,QuitFlag=True,Accelerate=False,StdoutFlag="readlines"):
        if len(cmdlist) > 0:
            for cmd in cmdlist:
                CmdObj = execCmd(cmd,self.logger)
                CmdObj.exeCmd(StdoutFlag)
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
        if status != 0 and not QuitFlag:
            self.logger.error("Cmd : \"%s\" ,Exit code : %s"%(cmd,self.exit))
            self.logger.error("Cmd : \"%s\" ,Stderr : %s"%(cmd,self.stderr))
            self.logger.error("fetch a error ,but don't quit")
        if status != 0 and QuitFlag:
            self.logger.error("Cmd : \"%s\" ,Exit code : %s"%(cmd,self.exit))
            self.logger.error("Cmd : \"%s\" ,Stderr : %s"%(cmd,self.stderr))
            self.logger.error("Exec Cmd fail,quit!")
            raise CustomVodException("ExecShellCmdFail","Execute Shell Command Exception")
            #sys.exit(self.status)  

# -------------------------------------- /
# 日志模块
# -------------------------------------- /
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

# -------------------------------------- / 
# 发邮件模块
# -------------------------------------- /
class SendMail(threading.Thread):
    def __init__(self,logger,subject,text):
        self.logger = logger
        self.subject = subject
        self.text = text
        
        self.FromAddr = "support@skygrande.com"
        self.SmtpServer = "smtp.exmail.qq.com"
        self.user = "support@skygrande.com"
        self.pwd = "1qaz2wsx`"
        self.ToAddr = "wye@skygrande.com"
        self.MailFlag = "微童年点播处理"
        
        threading.Thread.__init__(self)
    
    def run(self): 
        Mail_list = {"server":self.SmtpServer,
                     "fromAddr": "%s <%s>"%(Header(self.MailFlag,"utf-8"),self.FromAddr),
                     "user":self.user,
                     "passwd":self.pwd}
        msg = MIMEText(self.text,_charset="utf-8")
        msg["Subject"] = self.subject
        msg["From"] = Mail_list["fromAddr"]
        msg["To"] = self.ToAddr
        try:
            self.logger.info("Start send mail,subject is : %s , text is : %s"%(self.subject,self.text))
            send_smtp = smtplib.SMTP()
            send_smtp.connect(Mail_list["server"])
            send_smtp.login(Mail_list["user"],Mail_list["passwd"])
            send_smtp.sendmail(Mail_list["fromAddr"],self.ToAddr,msg.as_string())
            send_smtp.close()
            return True
        except Exception,e:
            self.logger.error("Send mail to %s fail,Error info : %s "%(self.ToAddr,e))

# -------------------------------------- /
# 获取直播流平均码率和平均时间
# -------------------------------------- /
def GetAvgbrAndAvgtime(TsDir,date,logger,ffprobe):
    ExeShellCmdObj=runCmd(logger)
    SampleNum = 10
    TsList = []
    TsDurationSum = 0
    TsBitrateSum = 0

    while True:
        RanNum = random.randint(1,8640)
        TsSegName = str(date) + "%05d"%RanNum + ".ts"
        TsSegPath = TsDir + "/" + TsSegName
        if os.path.isfile(TsSegPath) == True:
            ExeShellCmdObj.run(["%s -v quiet -show_format -print_format json %s"%(ffprobe,TsSegPath)],StdoutFlag="read")
            TsMetaData = ujson.decode(ExeShellCmdObj.stdout)["format"]
            if TsMetaData.has_key("duration") and TsMetaData.has_key("bit_rate"):
                TsList.append(TsSegName)
                if len(TsList) == SampleNum:break
                    
    TsSegPath = TsDir + "/" + TsList[0]
    ExeShellCmdObj.run(["%s -v quiet -show_format -print_format json %s"%(ffprobe,TsSegPath)],StdoutFlag="read")
    TsMetaData = ujson.decode(ExeShellCmdObj.stdout)["format"]
    TsDurationMax = float(TsMetaData["duration"])
    TsDurationMin = float(TsMetaData["duration"])
    TsBitrateMax = int(TsMetaData["bit_rate"])
    TsBitrateMin = int(TsMetaData["bit_rate"])   
    
    for TsSegName in TsList:
        TsSegPath = TsDir + "/" + TsSegName
        ExeShellCmdObj.run(["%s -v quiet -show_format -print_format json %s"%(ffprobe,TsSegPath)],StdoutFlag="read")
        TsMetaData = ujson.decode(ExeShellCmdObj.stdout)["format"]
        TsDuration = float(TsMetaData["duration"])
        TsBitrate = int(TsMetaData["bit_rate"])
        logger.info("TsBitrate:%s,TsTime:%s"%(TsBitrate/1024,TsDuration))
        if TsDuration > TsDurationMax:TsDurationMax = TsDuration
        if TsDuration < TsDurationMin:TsDurationMin = TsDuration
        if TsBitrate > TsBitrateMax:TsBitrateMax = TsBitrate
        if TsBitrate < TsBitrateMin:TsBitrateMin = TsBitrate
        TsDurationSum = TsDurationSum + TsDuration 
        TsBitrateSum = TsBitrateSum + TsBitrate
    TsAvgbr = (TsBitrateSum-TsBitrateMax-TsBitrateMin)/(SampleNum-2)
    TsAvgtime = (TsDurationSum-TsDurationMax-TsDurationMin)/(SampleNum-2)
    logger.info("TsBitrateMax:%s,TsBitrateMin:%s,TsDurationMax:%s,TsDurationMin:%s.TsAvgBitrate:%s,TsAvgTime:%s"%(TsBitrateMax/1024,TsBitrateMin/1024,TsDurationMax,TsDurationMin,TsAvgbr/1024,TsAvgtime))
    return TsAvgbr,TsAvgtime

# ------------------------------------- /
# 检查TS文件合法性
# ------------------------------------- /
def TsIsVaild(TsPath,TsAvgbr,TsAvgtime,ffprobe,logger):
    if os.path.isfile(TsPath):
        ExeShellCmdObj=runCmd(logger)
        try:
            ExeShellCmdObj.run(["%s -v quiet -show_format -print_format json %s"%(ffprobe,TsPath)],StdoutFlag="read")
        except Exception,e:
            logger.info("Fetch a exception in check ts isvaild,But program don't quit,Continue handle other ts,Exception is : \n %s"%e)
            return False
        TsMetaData = ujson.decode(ExeShellCmdObj.stdout)["format"]
        if TsMetaData.has_key("duration") and TsMetaData.has_key("bit_rate"):
            TsDuration = float(TsMetaData["duration"])
            TsBitrate = int(TsMetaData["bit_rate"])
            if -150 < TsBitrate/1024 - TsAvgbr/1024 < 150 and -4 < int(TsDuration - TsAvgtime) < 4:
                return True
            else:
                logger.warning("Ts Is Invaild,Discard it. \n \
                             TsAvgtime :  %s,  \n \
                             TsAvgbr :    %s,  \n \
                             TsDuration : %s,  \n \
                             TsBitrate : %s,   \n \
                             TsPath : %s,      \n \
                            "%(TsAvgtime,TsAvgbr/1024,TsDuration,TsBitrate/1024,TsPath))
                return False
        else:
            return False
    else:
        return False
    
# ------------------------------------- /
# 与MYSQL,REDIS等数据存储系统交互模块
# ------------------------------------- /
class DataInter(object):
    def __init__(self,logger):
        config = ConfigParser.ConfigParser()
        config.read(os.path.dirname(os.path.abspath(sys.argv[0]))+"/config.ini")
    
        self.MysqlServer = config.get("mysql","MysqlServer") 
        self.MysqlPort = config.get("mysql","MysqlPort")
        self.MysqlDB = config.get("mysql","MysqlDB")
        self.MysqlUser = config.get("mysql","MysqlUser")
        self.MysqlPasswd = config.get("mysql","MysqlPasswd")      
                
        self.RedisServer = config.get("redis","RedisServer")
        self.RedisPort = int(config.get("redis","RedisPort"))
        self.RedisDB = int(config.get("redis","RedisDB"))
        
        self.HDFSInterfaces = config.get("HDFS","HDFSInterfaces")
        self.HDFSInterfacePort = config.get("HDFS","HDFSInterfacePort")
        self.HDFSUser = config.get("HDFS","HDFSUser")        
        
        self.logger = logger

    # --/
    #    获取摄像头数据库状态
    #    -1 -- 未绑定
    #     0 -- 初始化成功或停止
    #     1 -- 启动
    #     2 -- 未找到记录
    #     3 -- 异常
    # --/
    def GetCamDBStatus(self,cid):
        try:
            DBConn = MySQLdb.connect(host=self.MysqlServer,user=self.MysqlUser,passwd=self.MysqlPasswd)
            DBCursor = DBConn.cursor()
            DBConn.select_db(self.MysqlDB)  
            SqlResultNum = DBCursor.execute('select status from t_device where index_code=%s',(cid))
            if SqlResultNum == 0 or SqlResultNum == None:
                return 2
            else:
                SqlResultVal = DBCursor.fetchone()
                DBConn.commit()
                return SqlResultVal[0]
        except exception,e:
       
            return 3
        finally:
            DBConn.close()
            DBCursor.close()  
        
    def GetOidRidandVodsavedays(self,cid):
        #  ---------------------------- /
        #  从MYSQL数据库获取摄像头的机构ID,场景ID,点播记录保存多少天.
        # ----------------------------- /
        try:
            DBConn = MySQLdb.connect(host=self.MysqlServer,user=self.MysqlUser,passwd=self.MysqlPasswd)
            DBCursor = DBConn.cursor()
            DBConn.select_db(self.MysqlDB)        
            SqlResultNum = DBCursor.execute('select unit_code,store_time_len,region_id from t_device where index_code=%s',(cid))
            if SqlResultNum == 0 or SqlResultNum == None:
                self.logger.error("No find related record in t_device for cid %s,Program not quit,Continue handle other's cid"%cid)
                return None
            else:            
                SqlResultVal = DBCursor.fetchone()
                DBConn.commit()
                return SqlResultVal
        except exception,e:
            self.logger.error("Obtain cid base info fail!!!")
            sys.exit()
        finally:
            DBConn.close()
            DBCursor.close()
    
    def GetCidVodPlan(self,cid):
        RedisPool = redis.ConnectionPool(host=self.RedisServer,port=self.RedisPort,db=self.RedisDB)
        Redata = redis.Redis(connection_pool=RedisPool)
        VodPlanRawData = Redata.get("%s_vod"%cid)
        if VodPlanRawData == None:
            self.logger.error("No find related key in redis pool for cid %s,Program not quit,Continue handle other's cid"%cid)
            return None
        else:
            return VodPlanRawData

    def GetCidIsBindKQ(self,cid):
        try:
            RedisPool = redis.ConnectionPool(host=self.RedisServer,port=self.RedisPort,db=self.RedisDB)
            Redata = redis.Redis(connection_pool=RedisPool)
            Value = Redata.get("%s_bind_kaoqin"%cid)
            if Value == None or int(Value) == 0:
                return False
            else:
                return True
        except Exception,e:
            return False

    def GetVodHandleStatus(self,vod):
        # ---------------------------- /
        # VOD HANDLE STATUS DESCRIPTION:
        #        -1 : 还没进行处理
        #         0 ：正在处理
        #         1 ：处理失败
        #         2 ：处理成功
        # ----------------------------- /
        try:
            DBConn = MySQLdb.connect(host=self.MysqlServer,user=self.MysqlUser,passwd=self.MysqlPasswd)
            DBCursor = DBConn.cursor()
            DBConn.select_db(self.MysqlDB)
            VodSplitList = vod.split("-") 
            cid = VodSplitList[6]
            VodDate = VodSplitList[4]
            CourseId = VodSplitList[2]
            sql = 'select handlestatus from t_video where device_id=%s and rec_date=%s and course_id=%s'
            SqlResultNum = DBCursor.execute(sql,(cid,VodDate,CourseId))      
            if SqlResultNum == 0:
               return -1
            elif SqlResultNum == 1:
              handlestatus = int(DBCursor.fetchone()[0])
              DBConn.commit()
              return handlestatus
            else:
                self.logger.error("Fatal Error,In table t_video have dup record,quit!!!")
                sys.exit()
        except Exception,e:
            self.logger.error("Fatal Error,Connect to mysql exception for get vod plan handlestatus : %s ,Error is : %s"%(vod,e))
            sys.exit()
        finally:
            DBConn.close()
            DBCursor.close()            
    
    def UpdateVodHandleStatus(self,vod,handlestatus):
        try:
            DBConn = MySQLdb.connect(host=self.MysqlServer,user=self.MysqlUser,passwd=self.MysqlPasswd)
            DBCursor = DBConn.cursor()
            DBConn.select_db(self.MysqlDB)
            VodSplitList = vod.split("-")
            cid = VodSplitList[6]
            VodDate = VodSplitList[4]
            CourseId = VodSplitList[2]            
            sql = 'update t_video set handlestatus=%s where device_id=%s and rec_date=%s and course_id=%s'
            paras = (int(handlestatus),cid,VodDate,CourseId)
            DBCursor.execute(sql,paras)
            DBConn.commit()          
        except Exception,e:
            self.logger.error("Fatal Error,Connect to mysql exception for update vod plan handlesatus : %s,Error is : %s"%(vod,e))
            sys.exit()
        finally:
            DBConn.close()
            DBCursor.close()            

    def InsertVodHandleStatus(self,vod,handlestatus):
        try:
            DBConn = MySQLdb.connect(host=self.MysqlServer,user=self.MysqlUser,passwd=self.MysqlPasswd)
            DBCursor = DBConn.cursor()
            DBConn.select_db(self.MysqlDB)
            VodSplitList = vod.split("-")
            VodStartTime = VodSplitList[0]
            VodEndTime =  VodSplitList[1]
            CourseId = VodSplitList[2] 
            VodSaveDays = VodSplitList[3]
            VodDate = VodSplitList[4]
            oid = VodSplitList[5]
            cid = VodSplitList[6]
            rid = VodSplitList[7]
            FileName = VodDate + VodStartTime.split(":")[0] + VodStartTime.split(":")[1] + VodEndTime.split(":")[0] + VodEndTime.split(":")[1] + ".m3u8"
            VodExpireDate = (datetime.datetime.strptime(VodDate,"%Y%m%d") + datetime.timedelta(days=int(VodSaveDays))).strftime("%Y%m%d")
            sql = 'insert into t_video (scence_id,device_id,instu_id,rec_date,start_time,end_time,file_name,expire_date,course_id,handlestatus) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'  
            paras = (rid,cid,oid,VodDate,VodStartTime,VodEndTime,FileName,VodExpireDate,CourseId,0)
            DBCursor.execute(sql,paras)
            DBConn.commit()          
        except Exception,e:
            self.logger.error("Fatal Error,Connect to mysql exception for insert vod plan record : %s,Error is : %s"%(vod,e))
            sys.exit()
        finally:
            DBConn.close()
            DBCursor.close()            
     
    def DelExpireVod(self,ExpireDate):
         try:
             DBConn = MySQLdb.connect(host=self.MysqlServer,user=self.MysqlUser,passwd=self.MysqlPasswd)
             DBCursor = DBConn.cursor()
             DBConn.select_db(self.MysqlDB)
             sql = "select instu_id,device_id,rec_date from t_video where expire_date=%s"
             RecordNum = DBCursor.execute(sql,(ExpireDate))
             if RecordNum == 0:
                 self.logger.info("No expire vod in %s for all cid in local caiji server"%ExpireDate)
             elif RecordNum > 0:
                 for row in DBCursor.fetchall():
                     oid = row[0]
                     cid = row[1]
                     VodGenDate = row[2]
                     self.logger.info("for cid:%s,vod create in %s will be delete"%(cid,VodGenDate))
                     HdfsSavePath = "/vod/%s/%s/%s"%(oid,cid,VodGenDate)
                     WebHdfsObj = WebHadoop(self.HDFSInterfaces,self.HDFSInterfacePort,self.HDFSUser,self.logger)
                     if WebHdfsObj.remove(str(HdfsSavePath)):
                         self.logger.info("expire vod file delete success!")
                     else:
                         self.logger.warning("for cid %s,vod create in %s delete fail"%(cid,VodGenDate))  
                 #删除数据库中过期VOD记录
                 sql = "delete from t_video where expire_date=%s"
                 paras = (ExpireDate)
                 RetValNum = DBCursor.execute(sql,(ExpireDate))
                 if RetValNum == RecordNum:
                     self.logger.info("Del expire vod record in db success!!!")
                 else:
                     self.logger.error("Del expire vod record in db fail!!!,select record is : %s,delete record is : %s"%(RecordNum,RetValNum))                    
             else:
                 self.logger.error("Obtain expire vod record fail,no quit!!!")                 
         except Exception,e:
             self.logger.error("Obtain expire vod record exception.no quit!!!")
         finally:
             DBConn.close()
             DBCursor.close()

    def DelFailVodRecordFromMysql(self,date):
         try:
             DBConn = MySQLdb.connect(host=self.MysqlServer,user=self.MysqlUser,passwd=self.MysqlPasswd)
             DBCursor = DBConn.cursor()
             DBConn.select_db(self.MysqlDB)
             sql = "delete from t_video where rec_date=%s and handlestatus=0"
             paras = (date)
             RetValNum = DBCursor.execute(sql,(date))
             self.logger.info("Del handle fail vod record of %s from mysql success!!!"%date)
         except Exception,e:
             self.logger.error("Del handle fail vod recode of %s from mysql fail,no quit!!!"%date) 
         finally:
             DBConn.close()
             DBCursor.close()
                  
if __name__ == "__main__":
    pass
    #logger = GetLog("test")        
    #print DataInter(logger).GetOidandVodsavedays("Cvvvlv22")
    #DataInter(logger).test("20140730")
        
     
        
        
        
        
        
        
        
        
        
        
