#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# ------------------------------------------------
# Purpose:
#    Clean up the specified log file and do the following
# +  Rename and compress the log file
# +  If the Compressed log file is $SaveDayNums days ago,it is deleted.
# -------------------------------------------------
# @Author: weiye
# @Date : 2016-06-13
# @Complete basic functions
# -------------------------------------------------

import os
import sys
import logging
import datetime
import subprocess
import ConfigParser
import logging.handlers

MV = "/bin/mv"
RM = "/bin/rm"
TAR = "/bin/tar"

def GetLogHandler(logflag,loglevel="debug"):
    logger = logging.Logger(logflag)
    logfile = "/var/log/%s.log"%logflag
    hdlr = logging.handlers.RotatingFileHandler(logfile, maxBytes = 5*1024*1024, backupCount = 5)
    formatter = logging.Formatter("%(asctime)s -- [ %(name)s ] -- %(levelname)s -- %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)    
    if loglevel == "debug": 
        logger.setLevel(logging.DEBUG)
    elif loglevel == "info":
        logger.setLevel(logging.INFO)
    elif loglevel == "warning":
        logger.setLevel(logging.WARNING)
    elif loglevel == "error":
        logger.setLevel(logging.ERROR)
    elif loglevel == "critical":
        logger.setLevel(logging.CRITICAL)
    return logger


def ParseConfigFile():
    config = ConfigParser.ConfigParser()
    config.read(os.path.dirname(os.path.abspath(sys.argv[0]))+"/config.ini")
    LogPathList = [key[1] for key in config.items("LogPath")]
    SaveDayNums = int(config.get("Global","LogSaveNums")) 
    return LogPathList , SaveDayNums


def RenameAndCompressLog(LogPath):
    LogDir = os.path.dirname(LogPath)
    LogName = os.path.basename(LogPath)
    PreDate = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%Y%m%d")
    LogRename = LogName+"."+PreDate
    Cmd = "cd %s && %s %s %s && %s zcf %s.tar.gz %s && %s -f %s"
    CmdStr = Cmd%(LogDir,MV,LogName,LogRename,TAR,LogRename,LogRename,RM,LogRename)
    ReturnCode = subprocess.call(CmdStr,shell=True)
    if ReturnCode == 0:
        return True,CmdStr
    else:
        return False,CmdStr


def DelExpireCompressLog(LogPath,SaveDayNums):
    LogDir = os.path.dirname(LogPath)
    LogName = os.path.basename(LogPath)
    ExpireDate = (datetime.datetime.now()-datetime.timedelta(days=SaveDayNums)).strftime("%Y%m%d")
    ExpireLogName =  LogName + "." + ExpireDate + ".tar.gz"
    ExpireLogPath = LogDir + "/" + ExpireLogName
    if os.path.isfile(ExpireLogPath):
        Cmd = "cd %s && %s -f %s"
        CmdStr = Cmd%(LogDir,RM,ExpireLogName)
        ReturnCode = subprocess.call(CmdStr,shell=True)
        if ReturnCode == 0:
            return True,CmdStr
        else:
            return False,CmdStr
    else:
        return False , "%s No Expire Log File"%LogName


if __name__ == "__main__":
    logger = GetLogHandler("CleanUpLog")
    try:
        LogPathList , SaveDayNums = ParseConfigFile()
        for LogPath in LogPathList:
            if os.path.isfile(LogPath):
                ExecInfo = RenameAndCompressLog(LogPath)
                logger.debug(ExecInfo)
                ExecInfo = DelExpireCompressLog(LogPath,SaveDayNums)
                logger.debug(ExecInfo)
            else:
                logger.error("%s Log File Is Not Exist"%LogPath)
    except Exception,e:
        logger.error("Clean Up Log Exception , Error is %s"%e)


    









