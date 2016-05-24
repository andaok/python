#!/usr/bin/env python
# -*- encoding:utf-8 -*-


#-------------------------------------------------------- /
# @author:wye
# @date:20151216
# @Copy Satisfaction Ts and M3u8 File To Hdfs By The Tool Crontab For 
# +Kaoqin Camera. 
#-------------------------------------------------------- /


import os
import sys
import time
import redis
import MySQLdb
import datetime
import subprocess
import logging
import logging.handlers
from WebHDFSApi import WebHadoop


# ----------------------- /
# LOG FUNCTION
# ----------------------- /
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


# ------------------------ /
# GET CAMERA CIDS LIST OF RUNNING IN LOCAL SERVER
# ------------------------ /
def GetCidList(logger):
    CidsNameFile = "/opt/caiji/script/vodconfig"
    ScriptHome = os.path.dirname(os.path.abspath(sys.argv[0]))
    RetObj = subprocess.Popen("/bin/bash %s/ScanLocalCidsFile.sh %s"%(ScriptHome,CidsNameFile),shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    CidsStr = RetObj.stdout.read().strip('\n')
    if CidsStr == "" or CidsStr == None:
        logger.error("No Camera Run In This CaiJi Server,Quit!!!")
        sys.exit()
    else:
        CidList = CidsStr.split(",")
        return CidList


# ------------------------ /
# HANDLE ATTENDANCE DATA FOR EACH CAMERA
# ------------------------ /
class HandleKQDataPerCam(object):

    def __init__(self,date,cid,logger):

        self.logger = logger
        self.date = date
        self.cid = cid

        self.uid = None
        self.LocalFileDir = None
        self.HdfsFileDir = None

        self.CutTsTime = 10

        self.MysqlServer = "10.2.10.12"
        self.MysqlUser = "cloudiya"
        self.MysqlPasswd = "c10udiya"
        self.MysqlDB = "weitongnian" 

        self.RedisServer = "10.2.10.19"
        self.RedisPort = 6379
        self.RedisDB = 0


        self.WebHdfsObj = WebHadoop("10.2.0.8,10.2.0.10",14000,"cloudiyadatauser",logger)


    # ---------------------- /
    # GET UNIT ID OF THE KINDERGARTEN BIND TO CAMERA
    # ---------------------- /
    def GetCamBaseInfo(self):
        try:
            DBConn = MySQLdb.connect(host=self.MysqlServer,user=self.MysqlUser,passwd=self.MysqlPasswd)
            DBCursor = DBConn.cursor()
            DBConn.select_db(self.MysqlDB)        
            SqlResultNum = DBCursor.execute('select unit_code from t_device where index_code=%s',(self.cid))
            if SqlResultNum == 0 or SqlResultNum == None:
                raise Exception("No Find Related Record In t_device Table")
            else:            
                SqlResultVal = DBCursor.fetchone()
                DBConn.commit()
                unit_code = SqlResultVal[0]
                return unit_code
        except Exception,e:
            raise Exception("Connect To Mysql Exception,%s"%e)
        finally:
            DBConn.close()
            DBCursor.close()  
    
    
    # ----------------------- /
    # CHECK WHETHER THE CAMERA AND THE ATTENDANCE MACHINE BIND
    # ----------------------- /
    def IsCamBindKQ(self):
        try:
            RedisPool = redis.ConnectionPool(host=self.RedisServer,port=self.RedisPort,db=self.RedisDB)
            Redata = redis.Redis(connection_pool=RedisPool)
            Value = Redata.get("%s_bind_kaoqin"%self.cid)
            if Value == None or int(Value) == 0:
                return False
            else:
                return True
        except Exception,e:
            raise Exception("Connect To Redis Exception,%s"%e)


    # ---------------------- /
    # CAMERA OF BIND ATTENDANCE MACHINE WHETHER HAVE ATTENDANCE DATA IN REDIS 
    # ---------------------- /
    def IsHaveKQData(self):
        try:
            RedisPool = redis.ConnectionPool(host=self.RedisServer,port=self.RedisPort,db=self.RedisDB)
            Redata = redis.Redis(connection_pool=RedisPool)
            Value = Redata.exists("%s_kaoqin_%s"%(self.cid,self.date))
            if int(Value) == 0:
                return False
            else:
                return True
        except Exception,e:
            raise Exception("Connect To Redis Exception,%s"%e)

    # ---------------------- /
    # CHECK WHETHER EXIST RELATE DIR IN LOCAL AND HDFS
    # ---------------------- /
    def IsExistNeedDir(self):
        if os.path.isdir(self.LocalFileDir) == True:
            if self.WebHdfsObj.lsdir(self.HdfsFileDir):
                return True
            else:
                if self.WebHdfsObj.mkdir(str(self.HdfsFileDir)) == True:
                    return True
                else:
                    self.logger.error("Hdfs File Dir Create Fail")
                    return False
        else:
            self.logger.error("Local File Dir Not Exist")
            return False

    # ---------------------- /
    # GET ATTENDANCE DATA FROM REDIS
    # ---------------------- /
    def GetCamKQData(self):
        try:
            RedisPool = redis.ConnectionPool(host=self.RedisServer,port=self.RedisPort,db=self.RedisDB)
            Redata = redis.Redis(connection_pool=RedisPool)
            KQDataList = Redata.smembers("%s_kaoqin_%s"%(self.cid,self.date))
            if KQDataList == None:
                raise Exception("Camera Have Bind KaoQin Device,But Get KQData Fail From Redis")
            else:
                return KQDataList
        except Exception,e:
            raise Exception("Connect To Redis Exception,%s"%e)

    # --------------------- /
    # CALCULATION OF THE NEED TO COPY THE FILES
    # --------------------- /
    def CalNeedCopyFiles(self,KQDataList):
        NeedCopyFileList = []
        for TimeStamp_Attenance in KQDataList:
            self.logger.info(TimeStamp_Attenance)
            YmdHMSTime_ZeroPointTime = self.date + " " + "00:00:00"
            TimeStamp_ZeroPointTime = int(time.mktime(time.strptime(YmdHMSTime_ZeroPointTime, "%Y%m%d %H:%M:%S")))
            TimeDiffNum = int(TimeStamp_Attenance) - TimeStamp_ZeroPointTime
            OriTsSeg = TimeDiffNum/self.CutTsTime 
            TsSegList = [OriTsSeg-2,OriTsSeg-1]
            TmpStr = ""
            for TsSeg in TsSegList:
                NeedCopyFileList.append(self.date+"%05d.ts"%TsSeg)
                TmpStr = TmpStr + "%05d"%TsSeg
            NeedCopyFileList.append(self.date+TmpStr.strip()+".m3u8")
        return  set(NeedCopyFileList)


    # --------------------- /
    # COPY FILES FROM LOCAL DIR TO HDFS
    # --------------------- /
    def CopyFilesToHdfs(self,NeedCopyFileSet):
        for FileName in NeedCopyFileSet:
            LocalFilePath = self.LocalFileDir + "/" + FileName
            HdfsFilePath = self.HdfsFileDir + "/" + FileName
            self.WebHdfsObj.put_file(LocalFilePath,HdfsFilePath)
            self.logger.info("test")

    # --------------------- /
    # MAIN PROGRAM
    # --------------------- /
    def main(self):
        if self.IsCamBindKQ() == True:
            logger.info("------------------------------------- /")
            logger.info("Start Handle Camera %s"%self.cid)
            if self.IsHaveKQData() == True:
                self.uid = self.GetCamBaseInfo()
                self.LocalFileDir = "/Data" + "/" + self.uid + "/" + self.cid + "/media/" + self.date
                self.HdfsFileDir = "/kqvod" + "/" + self.uid + "/" + self.cid + "/" + self.date
                if self.IsExistNeedDir() == True:
                    KQDataList = self.GetCamKQData()
                    NeedCopyFileSet = self.CalNeedCopyFiles(KQDataList)
                    self.CopyFilesToHdfs(NeedCopyFileSet)
                else:
                    self.logger.error("Camera Have Bind KaoQin Device,But Relate Dir Not Exist")
            else:
                self.logger.error("Camera Have Bind KaoQin Device,But Get KQData Key Fail In Redis")


if __name__ == "__main__":
    logger = GetLog("CopyTsToHdfsForKQ")
    try:
        if len(sys.argv) == 1:
            Date = datetime.datetime.now().strftime("%Y%m%d")
            CidList = GetCidList(logger)
        elif len(sys.argv) == 2 and len(sys.argv[1]) == 8 and sys.argv[1].isdigit():
            Date = sys.argv[1]
            CidList = GetCidList(logger)
        elif len(sys.argv) == 3 and len(sys.argv[1]) == 8 and sys.argv[1].isdigit() and len(sys.argv[2]) == 8:
            Date = sys.argv[1]
            CidList = [sys.argv[2]]
        else:
            logger.error("Parameter does not meet the requirements,Program quit")
            sys.exit()

        for Cid in CidList:
            try:
                HandleObj = HandleKQDataPerCam(Date,Cid,logger)
                HandleObj.main()
            except IndexError,e:
                logger.warning("Handle Camera Exception,Continue To Other's Camera,Error Is %s"%e)
                continue
    except IndexError,e:
        logger.error("Program Exception Quit,Error is : %s"%e)
        sys.exit()

    
