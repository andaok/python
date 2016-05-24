#!/usr/bin/env python
# -*- encoding:utf-8 -*-


# ------------------------------
# @author:wye
# @date:20140713
# @camera manage,start,stop,restart and so on
# @date:20151214
# @Http api interface for rfid kaoqin video
# ------------------------------


import os
import time
import glob
import ujson
import random
import string
import datetime
import subprocess
import logging
import logging.handlers
from bottle import Bottle,run
from WebHDFSApi import WebHadoop

mybottle = Bottle()


#----------------------------------------------------------------------- /
#
#
#                           CAMERA MANAGE
#
#
#---------------------------------------------------------------------- /


@mybottle.route('/start/<cid>')
def start(cid):
        #Check whether the relevant processes already exist
        p = subprocess.Popen("/bin/ps -aux | grep ffmpeg | grep %s | grep -v grep | wc -l"%cid,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        pnum = int(p.stdout.read())
        if pnum == 0:
            #Start the process
            rcode = subprocess.call("/usr/bin/python /opt/caiji/script/ffstart.py  %s"%cid,shell=True,close_fds=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT )
            if int(rcode) == 0:
                return '{"status":0,"info":"Process start success"}'
            else:
                return '{"status":1,"info":"Process start fail"}'
        else:
            return '{"status":2,"info":"Process already exist!"}'
        
@mybottle.route('/init/<cid>')
def init(cid):
    #Initalize the environment,to prepare for the crawl stream
    rcode = subprocess.call("/bin/bash /opt/caiji/script/ffinit.sh  %s"%cid,shell=True,close_fds=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)
    if int(rcode) == 0:
        return '{"status":0,"info":"Init environment success!"}'
    else:
        return '{"status":1,"info":"Init environment fail!"}'

@mybottle.route('/stop/<cid>')
def stop(cid):
    #Check whether the relevant processes already exist
    p = subprocess.Popen("/bin/ps -aux | grep ff | grep %s | grep -v grep | wc -l"%cid,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    pnum = int(p.stdout.read())
    if pnum == 2 or pnum == 1:
        #Stop Process
        rcode = subprocess.call("/bin/bash /opt/caiji/script/ffstop.sh  %s"%cid,shell=True,close_fds=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)
        if int(rcode) == 0:
            return '{"status":0,"info":"Stop process success!"}'
        else:
            return '{"status":1,"info":"Stop process fail!"}'
    elif pnum == 0:
        return '{"status":2,"info":"Relevant process no find"}'
    else:
        return '{"status":3,"info":"Have multiple related processes"}'


@mybottle.route('/delete/<cid>')
def delete(cid):
    rcode = subprocess.call("/bin/bash /opt/caiji/script/ffdel.sh  %s"%cid,shell=True,close_fds=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)
    if int(rcode) == 0:
        return '{"status":0,"info":"Delete Camera success!"}'
    else:
        return '{"status":1,"info":"Delete Camera fail!"}'
        
@mybottle.route('/restart/<cid>')
def restart(cid):
    #restart process
    rcode = subprocess.call("/bin/bash /opt/caiji/script/ffrestart.sh %s"%cid,shell=True,close_fds=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)
    if int(rcode) == 0:
        return '{"status":0,"info":"restart process success!"}'
    else:
        return '{"status":1,"info":"restart process fail!"}'

@mybottle.route('/status/<cid>')
def status(cid):
    ptmp1 = subprocess.Popen("/bin/ps -aux | grep %s | grep -v grep | grep ffstart | wc -l"%cid,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    DaemonNum= int(ptmp1.stdout.read())
    ptmp2 = subprocess.Popen("/bin/ps -aux | grep %s | grep -v grep | grep ffmpeg | wc -l"%cid,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    FfmpegNum = int(ptmp2.stdout.read())
    if DaemonNum == 1 and FfmpegNum == 1:
        return '{"status":0,"info":"Living"}'
    elif DaemonNum == 1 and FfmpegNum == 0:
        return '{"status":1,"info":"WaitLiving Or Fault"}'
    elif DaemonNum == 0 and FfmpegNum == 0:
        return '{"status":2,"info":"No Find Any Related Process"}'
    elif DaemonNum == 0 and FfmpegNum == 1:
        return '{"status":3,"info":"Only Have FFmpeg Process"}'
    else:
        return '{"status":4,"info":"Other Fault"}'
    

#-------------------------------------------------------------------  /
#
# 
#               API INTERFACE FOR RFID KAOQIN VIDEO
#
#
#------------------------------------------------------------------- / 

# --------------------------- /
#
# Log Module
#
# --------------------------- /
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


# --------------------------- /
# 
# Execute Shell Command Module
#
# --------------------------- /
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



CutTsTime = 10
FFPROBE = "/usr/local/bin/ffprobe"

logger = GetLog("CjsHttpApi")
ExeShellCmdObj=runCmd(logger)
WebHdfsObj = WebHadoop("10.2.0.8,10.2.0.10",14000,"cloudiyadatauser",logger)


@mybottle.route('/getplaylist/<uid>/<cid>/<attents>')
def getplaylist(uid,cid,attents):
    try:
        if len(uid) == 6 and len(cid) == 8:
            try:
                TimeStamp_Attenance = int(attents)
            except ValueError:
                return '{"status":1,"info":"Parameters Format Error"}'

            Date = datetime.datetime.fromtimestamp(TimeStamp_Attenance).strftime("%Y%m%d")
            Today = datetime.datetime.now().strftime("%Y%m%d")

            # -------------------- /
            # For KaoQIn Video Request Today
            # -------------------- /
            if Date == Today:
                TsNameList,M3u8FileName,LocalM3u8FileName = CalMeetReqTsSegList(Date,TimeStamp_Attenance)
                logger.debug("%s-%s"%(TsNameList,M3u8FileName))
                return ResM3u8NameForToday(uid,cid,Date,TsNameList,M3u8FileName,LocalM3u8FileName,TimeStamp_Attenance)
            else:
                # ------------------- /
                # For KaoQin Video Request Before
                # ------------------- /
                # TsNameList,M3u8FileName = CalMeetReqTsSegList(Date,TimeStamp_Attenance)
                # return ResM3u8NameForBefore(uid,cid,Date,TsNameList,M3u8FileName)

                logger.error("SOS,Attendance Time Is The Day Before,Don't Handle")
                return '{"status":1,"info":"Attendance Time Is The Day Before"}'
        else:
            return '{"status":1,"info":"Parameters Format Error"}'
    except Exception, e:
        return '{"status":1,"info":"API Exception %s"}'%e



# ------------------------------------------------------- /
#
# Calculation Satisfy Condition For Ts Segment,
# Return Ts List And M3u8 File Name.
# [2015121105138.ts,2015121105139.ts,2015121105140.ts]
#
# ------------------------------------------------------- /
def CalMeetReqTsSegList(Date_Attenance,TimeStamp_Attenance):
    YmdHMSTime_ZeroPointTime = Date_Attenance + " " + "00:00:00"
    TimeStamp_ZeroPointTime = int(time.mktime(time.strptime(YmdHMSTime_ZeroPointTime, "%Y%m%d %H:%M:%S")))
    TimeDiffNum = TimeStamp_Attenance - TimeStamp_ZeroPointTime
    OriTsSeg = TimeDiffNum/CutTsTime
    TsSegList = [OriTsSeg-1,OriTsSeg,OriTsSeg+1]
    #TsSegList = [OriTsSeg-2,OriTsSeg-1,OriTsSeg]
    #TsSegList = [OriTsSeg-2,OriTsSeg-1]
    TsNameList = []
    TmpStr = ""
    for TsSeg in TsSegList:
        TsNameList.append(Date_Attenance+"%05d.ts"%TsSeg)
        TmpStr = TmpStr + "%05d"%TsSeg
    M3u8FileName = Date_Attenance+TmpStr.strip()+".m3u8"
    LocalM3u8FileName = M3u8FileName + "-" + str(int(time.time()*1000))
    return TsNameList , M3u8FileName , LocalM3u8FileName
    


# --------------------- /
# COPY FILES FROM LOCAL DIR TO HDFS
# --------------------- /
def CopyFilesToHdfs(LocalFileDir,HdfsFileDir,NeedCopyTsList,M3u8FileName,LocalM3u8FileName):
    # COPY TS FILES TO HDFS 
    for FileName in NeedCopyTsList:
        LocalFilePath = LocalFileDir + "/" + FileName
        HdfsFilePath = HdfsFileDir + "/" + FileName
        WebHdfsObj.put_file(LocalFilePath,HdfsFilePath)
    # COPY M3U8 FILE TO HDFS
    LocalFilePath = LocalFileDir + "/" + LocalM3u8FileName
    HdfsFilePath = HdfsFileDir + "/" + M3u8FileName
    WebHdfsObj.put_file(LocalFilePath,HdfsFilePath)


# ---------------------- /
# CHECK WHETHER EXIST RELATE DIR IN LOCAL AND HDFS
# ---------------------- /
def IsExistNeedDir(LocalFileDir,HdfsFileDir):
    if os.path.isdir(LocalFileDir) == True:
        if WebHdfsObj.mkdir(str(HdfsFileDir)) == True:
            return True
        else:
            logger.error("Hdfs File Dir Create Fail")
            return False
    else:
        logger.error("Local File Dir Not Exist")
        return False


# -------------------------------- /
#
# Response M3u8 File Name For Kaoqin Video Request Today
#
# -------------------------------- /
def ResM3u8NameForToday(uid,cid,date,TsNameList,M3u8FileName,LocalM3u8FileName,TimeStamp_Attenance):
    IsMeet = True
    TsDir = "/Data" + "/" + uid + "/" + cid + "/media/" + date
    LocalFileDir = TsDir
    HdfsFileDir = "/kqvod" + "/" + uid + "/" + cid + "/" + date

    if len(glob.glob(LocalFileDir+"/"+M3u8FileName+"-*")) == 0:
        if IsExistNeedDir(LocalFileDir,HdfsFileDir) == True:
            for TsName in TsNameList:
                TsPath = TsDir + "/" + TsName
                if os.path.isfile(TsPath) == False:
                    IsMeet = False
                    break
            if IsMeet == True:
                try:
                    GenM3u8FileForToday(TsDir,TsNameList,LocalM3u8FileName)
                    CopyFilesToHdfs(LocalFileDir,HdfsFileDir,TsNameList,M3u8FileName,LocalM3u8FileName)
                    return '{"status":0,"info":"%s"}'%M3u8FileName
                except Exception,e:
                    logger.error("Program Exception,Error Is %s"%e)
                    return '{"status":1,"info":"Program Exception %s"}'%e
            else:
                return '{"status":1,"info":"Video Ts File Not Found"}'
        else:
            return '{"status":1,"info":"Local Ts Dir No Exist Or Create Hdfs Dir Failure"}'
    else:
        return '{"status":0,"info":"%s"}'%M3u8FileName



# -------------------------------- /
#
# Response M3u8 File Name For Kaoqin Video Request Before
#
# -------------------------------- /
def ResM3u8NameForBefore(uid,cid,date,TsNameList,M3u8FileName):
    IsMeet = True
    IsDownLoadSuc = True
    TsDir = "/kqvod" + "/" + uid + "/" + cid + "/" + date
    M3u8FilePath = TsDir + "/" + M3u8FileName
    if WebHdfsObj.lsdir(TsDir):
        if WebHdfsObj.lsfile(M3u8FilePath) == False:
            for TsName in TsNameList:
                TsPath = TsDir + "/" + TsName
                if WebHdfsObj.lsfile(TsPath) == False:
                    IsMeet = False
                    break
            if IsMeet == True:
                # Create Local Tmp Dir
                TmpSaveDir = "/tmp" + "/" + "kqv_" + ''.join(random.sample(string.ascii_letters + string.digits,8))
                ExeShellCmdObj.run(["/bin/mkdir -p %s"%TmpSaveDir],StdoutFlag="read")
                # Copy Ts Files From Hdfs To Local Tmp Dir
                for TsName in TsNameList:
                    TsPath = TsDir + "/" + TsName
                    LocalTsPath = TmpSaveDir + "/" + TsName
                    if WebHdfsObj.get_file(LocalTsPath,TsPath) == False:
                        IsDownLoadSuc = False
                        break
                if IsDownLoadSuc == True:
                    GenM3u8FileForBefore(TsDir,TsNameList,M3u8FileName,TmpSaveDir)
                    return '{"status":0,"info":"%s"}'%M3u8FileName
                else:
                    return '{"status":1,"info":"Video Not Found"}'
        else:
            return '{"status":0,"info":"%s"}'%M3u8FileName   
    else:
        return '{"status":1,"info":"Ts Dir No Exist"}'


# ---------------------------- /
#
# Generate M3u8 File And Write To Ts Dir For Before
#
# ---------------------------- /
def GenM3u8FileForBefore(TsDir,TsNameList,M3u8FileName,TmpSaveDir):
    MaxDuration = CutTsTime
    M3u8FilePath = TsDir + "/" + M3u8FileName
    LocalM3u8FilePath = TmpSaveDir + "/" + M3u8FileName

    for TsName in TsNameList:
        LocalTsPath = TmpSaveDir+"/"+TsName
        ExeShellCmdObj.run(["%s -v quiet -show_format -print_format json %s"%(FFPROBE,LocalTsPath)],StdoutFlag="read")
        TsMetaData = ujson.decode(ExeShellCmdObj.stdout)["format"]
        if TsMetaData.has_key("duration"):
           TsDuration = TsMetaData["duration"]
        else:
           continue 
        if float(TsDuration) > MaxDuration:MaxDuration = float(TsDuration)
        # ----------------------------------- /
        # Middle part of m3u8 file:
        # #EXTINF:10.000000,
        # 2014090602161.ts
        # ----------------------------------- /
        cmd = "echo \"#EXTINF:%s,\" >> %s && echo \"%s\" >> %s"%(TsDuration,LocalM3u8FilePath,TsName,LocalM3u8FilePath)
        ExeShellCmdObj.run([cmd])
    # ---------------------------------------- /
    # Head part of m3u8 file:
    # #EXTM3U
    # #EXT-X-VERSION:3
    # #EXT-X-MEDIA-SEQUENCE:2161
    # #EXT-X-ALLOW-CACHE:YES
    # #EXT-X-TARGETDURATION:10
    # ---------------------------------------- /
    cmd = "sed -i \"1i #EXTM3U\"  %s &&"
    cmd = cmd + "sed -i \"2i #EXT-X-VERSION:3\"  %s &&"
    cmd = cmd + "sed -i \"3i #EXT-X-MEDIA-SEQUENCE:%s\" %s &&"
    cmd = cmd + "sed -i \"4i #EXT-X-ALLOW-CACHE:YES\"  %s &&"
    cmd = cmd + "sed -i \"5i #EXT-X-TARGETDURATION:%s\"  %s"
    cmdstr = cmd%(LocalM3u8FilePath,LocalM3u8FilePath,0,LocalM3u8FilePath,LocalM3u8FilePath,int(MaxDuration),LocalM3u8FilePath)
    ExeShellCmdObj.run([cmdstr])
    # --------------------------------------- /
    # Tail part of m3u8 file:
    # #EXT-X-ENDLIST
    # --------------------------------------- /
    cmd = "sed -i \'$a #EXT-X-ENDLIST\' %s "%LocalM3u8FilePath
    ExeShellCmdObj.run([cmd])
    
    # Upload M3u8 File To Hdfs
    WebHdfsObj.put_file(LocalM3u8FilePath,M3u8FilePath)

    # Remove Tmp Dir
    ExeShellCmdObj.run(["/bin/rm -rf %s"%TmpSaveDir])


# ---------------------------- /
#
# Generate M3u8 File And Write To Ts Dir For Today
#
# ---------------------------- /            
def GenM3u8FileForToday(TsDir,TsNameList,M3u8FileName):
    MaxDuration = CutTsTime
    M3u8FilePath = TsDir + "/" + M3u8FileName

    #@ If the m3u8 file exist,Empty it.
    cmd = ": > %s"%M3u8FilePath
    ExeShellCmdObj.run([cmd])

    for TsName in TsNameList:
        TsPath = TsDir+"/"+TsName
        ExeShellCmdObj.run(["%s -v quiet -show_format -print_format json %s"%(FFPROBE,TsPath)],StdoutFlag="read")
        TsMetaData = ujson.decode(ExeShellCmdObj.stdout)["format"]
        if TsMetaData.has_key("duration"):
           TsDuration = TsMetaData["duration"]
        else:
           continue 
        if float(TsDuration) > MaxDuration:MaxDuration = float(TsDuration)
        # ----------------------------------- /
        # Middle part of m3u8 file:
        # #EXTINF:10.000000,
        # 2014090602161.ts
        # ----------------------------------- /
        cmd = "echo \"#EXTINF:%s,\" >> %s && echo \"%s\" >> %s"%(TsDuration,M3u8FilePath,TsName,M3u8FilePath)
        ExeShellCmdObj.run([cmd])
    # ---------------------------------------- /
    # Head part of m3u8 file:
    # #EXTM3U
    # #EXT-X-VERSION:3
    # #EXT-X-MEDIA-SEQUENCE:2161
    # #EXT-X-ALLOW-CACHE:YES
    # #EXT-X-TARGETDURATION:10
    # ---------------------------------------- /
    cmd = "sed -i \"1i #EXTM3U\"  %s &&"
    cmd = cmd + "sed -i \"2i #EXT-X-VERSION:3\"  %s &&"
    cmd = cmd + "sed -i \"3i #EXT-X-MEDIA-SEQUENCE:%s\" %s &&"
    cmd = cmd + "sed -i \"4i #EXT-X-ALLOW-CACHE:YES\"  %s &&"
    cmd = cmd + "sed -i \"5i #EXT-X-TARGETDURATION:%s\"  %s"
    cmdstr = cmd%(M3u8FilePath,M3u8FilePath,0,M3u8FilePath,M3u8FilePath,int(MaxDuration),M3u8FilePath)
    ExeShellCmdObj.run([cmdstr])
    # --------------------------------------- /
    # Tail part of m3u8 file:
    # #EXT-X-ENDLIST
    # --------------------------------------- /
    cmd = "sed -i \'$a #EXT-X-ENDLIST\' %s "%M3u8FilePath
    ExeShellCmdObj.run([cmd])
    

application = mybottle





