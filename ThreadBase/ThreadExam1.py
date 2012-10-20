# -*- encoding:utf-8 -*-

'''
Created on Jun 9, 2012

@author: wye

'''

import os
import sys
import time
import stat
import signal
import struct
import fcntl
import socket
import commands
import logging

try:
    from threading import Thread
except ImportError:
    from dummy_threading import Thread

# not using subprocess package to maintain at least python 2.3 compat.
from popen2 import Popen3

#local imports
#from ctx_exceptions import UnexpectedError, IncompatibleEnvironment
#from ctx_logging import getlog



def getlog(logfile="/tmp/log.log"):
    logger = logging.Logger("logrecord")
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter("%(asctime)s -- %(levelname)s -- %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger


class SimpleRunThread(Thread):
    """Run a command with timeout options, delay, stdin, etc."""
    
    def __init__(self, cmd, killsig=-1, killtime=0, stdin=None, delay=None, log_override=None):
        """Populate the thread.
        
        Required parameters:
        
        * cmd -- command to run
        
        Keyword parameters:
        
        * killsig -- signum to kill with, default is unset 
        (needed if you set a killtime)
        
        * killtime -- secs (float or int) to wait before kill, default is 
        unset (if set, needs killsig parameter)
        
        * stdin -- optional stdin to push, default is unset
        
        * delay -- secs (float or int) to wait before invoking cmd
        
        Properties available:
        
        * stdout -- stdout data or None
        
        * stderr -- stderr data or None
        
        * killed -- boolean, set True if cmd was killed
        
        * exception -- if kill won't work
        
        """
        
        Thread.__init__(self)
        self.cmd = cmd
        self.stdin = stdin
        self.killsig = killsig
        self.killtime = float(killtime)
        self.delay = delay
        self.exception = None
        self.exit = None
        self.stdout = None
        self.stderr = None
        self.killed = False
        self.log = getlog()
        
    def run(self):
        if self.delay:
            self.log.debug("delaying for %.3f secs: '%s'" % (self.delay, self.cmd))
            time.sleep(self.delay)
        self.log.debug("program starting '%s'" % self.cmd)
        p = Popen3(self.cmd, True)
        
        if self.stdin:
            if p.poll() == -1:
                p.tochild.write(self.stdin)
                p.tochild.flush()
                p.tochild.close()
                #log.debug("wrote '%s' to child" % self.stdin)
            else:
                self.log.error("child exited before stdin was written to")
                
        done = False
        while not done and self.killtime > 0:
            time.sleep(0.2)
            if p.poll() != -1:
                done = True
            self.killtime -= 0.2
            
        if not done and self.killsig != -1:
            try:
                os.kill(p.pid, self.killsig)
                self.killed = True
            except OSError, e:
                self.log.exception("problem killing")
                self.exception = e
                return
                
        status = p.wait()
        
        if os.WIFSIGNALED(status):
            self.exit = "SIGNAL: " + str(os.WTERMSIG(status))
        elif os.WIFEXITED(status):
            self.exit = str(os.WEXITSTATUS(status))
        else:
            self.exit = "UNKNOWN"
            
        self.stdout = p.fromchild.read()
        self.stderr = p.childerr.read()
        p.fromchild.close()
        p.childerr.close()
        self.log.debug("program ended: '%s'" % self.cmd)

      
def runexe(cmd, killtime=2.0, retry=0):
    """Run a system program.
    
    Required parameter:
    
    * cmd -- command to run, string
    
    * retry -- how many retry we will do when the exit status is non-zero
    Default is 0.
    
    Keyword parameter:
    
    * killtime -- how many seconds to wait before SIGKILL (int or float)
    Default is 2.0 seconds.
    
    Return (exitcode, stdout, stderr)
    
    * exitcode -- string exit code or msg
    
    * stdout -- stdout or None
    
    * stderr -- stderr or None
    
    Raises IncompatibleEnvironment for serious issue (but not on non-zero exit)
    
    """
    
    for i in range(retry+1):
        if killtime > 0:
            thr = SimpleRunThread(cmd, killsig=signal.SIGKILL, killtime=killtime)
        else:
            thr = SimpleRunThread(cmd)
        thr.start()
        thr.join()
    
        # sudo child won't take signals
        if thr.exception:
            #raise IncompatibleEnvironment(str(thr.exception))
            raise Exception(str(thr.exception))

        if thr.exit == "0":
            break
        else:
            time.sleep(0.5)
        
    return (thr.exit, thr.stdout, thr.stderr)





