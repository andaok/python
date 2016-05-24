#!/usr/bin/env python
# -*- encoding:utf-8 -*-

'''
Created on Nov 23, 2012

@author: wye

Copyright @ 2011 - 2012  Cloudiya Tech . Inc 
'''

import os
import sys
import time
import pickle
import logging
import operator
import subprocess

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
        
        cmdobj = subprocess.Popen(self.cmd,shell=True,stderr=subprocess.PIPE)
        
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
        
        if os.WIFSIGNALED(status):
            self.exit = "SIGNAL: " + str(os.WTERMSIG(status))
        elif os.WIFEXITED(status):
            self.exit = str(os.WEXITSTATUS(status))
        else:
            self.exit = "UNKNOWN"
        
        self.status = status
        self.stderr = cmdobj.stderr.read()
        
        cmdobj.stderr.close()
        
        self.log.debug("Cmd run end : %s "%self.cmd)
        
#######################################

class runCmd():
    def __init__(self,logger):
        self.logger = logger

    def run(self,cmdlist,QuitFlag=True,Accelerate=False):
        if len(cmdlist) > 0:
            for cmd in cmdlist:
                CmdObj = execCmd(cmd,self.logger)
                CmdObj.exeCmd()
                if CmdObj.status != 0 and not QuitFlag:
                    self.logger.error("Cmd : \"%s\" ,Exit code : %s"%(cmd,CmdObj.exit))
                    self.logger.error("Cmd : \"%s\" ,Stderr : %s"%(cmd,CmdObj.stderr))
                    self.logger.error("fetch a error ,but don't quit")
                if CmdObj.status != 0 and QuitFlag:
                    self.logger.error("Cmd : \"%s\" ,Exit code : %s"%(cmd,CmdObj.exit))
                    self.logger.error("Cmd : \"%s\" ,Stderr : %s"%(cmd,CmdObj.stderr))
                    self.logger.error("Exec Cmd fail,quit!")
                    sys.exit()
 
########################################

def getlog(VideoFileNameAlias,logfile="/tmp/videohandle.log",loglevel="info"):
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