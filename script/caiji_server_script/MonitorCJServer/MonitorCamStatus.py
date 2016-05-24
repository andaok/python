#!/usr/bin/env python
# -*- encoding:utf-8 -*-

#########################################
# Purpose:
#       this is daemon process for send cameras
#+      status info to carbon,in order to draw a state
#+      diagram in graphite.
# 
# @ Write  by wye in 2014.08.18
# @ Copyright@2014 cloudiya technology
# @ 2015-04-24
# @ Improve send mail function,The same message is sent only once.
##########################################

import os
import sys
import time
import socket
import fcntl
import struct
import syslog
import MySQLdb
import hashlib
import subprocess
import smtplib
import threading
from email.header import Header
from email.mime.text import MIMEText
#from socket import socket

# --/
#    获取本采集服务器IP地址
# --/

def _ifinfo(sock, addr, ifname):
    iface = struct.pack('256s', ifname[:15])
    info = fcntl.ioctl(sock.fileno(), addr, iface)
    if addr == 0x8927:
        hwaddr = []
        for char in info[18:24]:
            if len(hex(ord(char))[2:]) == 1:
                str = (hex(ord(char))[2:]*2).upper()
            else: 
                str = (hex(ord(char))[2:]).upper()
            hwaddr.append(str)
        return ':'.join(hwaddr)
    else:
        return socket.inet_ntoa(info[20:24])

def ifconfig(ifname):
    ifreq = {'ifname': ifname}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ifreq['addr'] = _ifinfo(sock, 0x8915, ifname) # SIOCGIFADDR
        ifreq['brdaddr'] = _ifinfo(sock, 0x8919, ifname) # SIOCGIFBRDADDR
        ifreq['netmask'] = _ifinfo(sock, 0x891b, ifname) # SIOCGIFNETMASK
        ifreq['hwaddr'] = _ifinfo(sock, 0x8927, ifname) # SIOCSIFHWADDR
    except:
        pass
    sock.close()
    return ifreq['addr']

# --/
#    发邮件
# --/

class SendMail(threading.Thread):
    
    def __init__(self,subject,text):
        self.subject = subject
        self.text = text
        
        self.FromAddr = "support@skygrande.com"
        self.SmtpServer = "smtp.exmail.qq.com"
        self.user = "support@skygrande.com"
        self.pwd = "1qaz2wsx`"
        self.ToAddr = "wye@skygrande.com"
        self.MailFlag = "微童年采集进程监控"
        
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
            send_smtp = smtplib.SMTP()
            send_smtp.connect(Mail_list["server"])
            send_smtp.login(Mail_list["user"],Mail_list["passwd"])
            send_smtp.sendmail(Mail_list["fromAddr"],self.ToAddr,msg.as_string())
            send_smtp.close()
            return True
        except Exception,e:
            syslog.syslog("Send mail to %s fail,Error info : %s "%(self.ToAddr,e))


# --/
#    发送数据去监控主机并发邮件报警
# --/

class SendCamStaToMonServer():
    
    def __init__(self):
        
        self.CidRestartTimePoint = {}
        self.CidList = []

        self.CidsNameFile = "/opt/caiji/script/vodconfig"
        self.CARBON_SERVER = "10.1.0.254"
        self.CARBON_PORT = 2003
        self.delay = 60
        
        self.ServerIPAddr = "_".join(ifconfig("eth0").split("."))
        self.ScriptHome = os.path.dirname(os.path.abspath(sys.argv[0]))

        self.MysqlServer = "10.2.10.12"
        self.MysqlUser = "cloudiya"
        self.MysqlPasswd = "c10udiya"
        self.MysqlDB = "68baobao"
        

        self.StatusFlag = {}


    def md5(self,str):

        """return string md5 value"""

        m = hashlib.md5()   
        m.update(str)
        return m.hexdigest()


    # -- /
    #     得到运行在本采集服务器的Cameras的cid
    # -- /
    def GetCidList(self):
        syslog.openlog("MonitorCamStatus") 
        RetObj = subprocess.Popen("/bin/bash %s/ScanLocalCidsFile.sh %s"%(self.ScriptHome,self.CidsNameFile),shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        CidsStr = RetObj.stdout.read().strip('\n')
        if CidsStr == "" or CidsStr == None:
            syslog.syslog("No Camera Run In This CaiJi Server,Quit!!!")
            sys.exit()
        else:
            self.CidList = CidsStr.split(",")

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
            syslog.syslog("Obtain %s Status Exception From Mysql,Error is %s"%(cid,e))
            return 3
        finally:
            DBConn.close()
            DBCursor.close()  

    
    def IsSendMail(self,ProStatus,cid):

        """ 
        Whether to send mail depending on Related process status and Previously send mail status 
        @ Add in 2015-4-24
        """

        if ProStatus in [0,1]:
            if self.StatusFlag.has_key(cid) and self.StatusFlag[cid] == False:
                MailObj = SendMail("Process Status Back To Normal","%s -- %s"%(self.ServerIPAddr,cid))
                MailObj.start()
                self.StatusFlag[cid] = True
        elif ProStatus == 2 and self.GetCamDBStatus(cid) == 1:
            if self.StatusFlag.has_key(cid):
                if self.StatusFlag[cid] == True:
                   MailObj = SendMail("Process Status Exception","%s -- %s"%(self.ServerIPAddr,cid))
                   MailObj.start()
                   self.StatusFlag[cid] = False
            else:
                MailObj = SendMail("Process Status Exception","%s -- %s"%(self.ServerIPAddr,cid))
                MailObj.start()
                self.StatusFlag[cid] = False            
            
        elif ProStatus in [3,4]:
            if self.StatusFlag.has_key(cid):
                if self.StatusFlag[cid] == True:
                   MailObj = SendMail("Process Status Exception","%s -- %s"%(self.ServerIPAddr,cid))
                   MailObj.start()
                   self.StatusFlag[cid] = False
            else:
                MailObj = SendMail("Process Status Exception","%s -- %s"%(self.ServerIPAddr,cid))
                MailObj.start()
                self.StatusFlag[cid] = False
           

    # -- /
    #     获取进程相关信息
    # -- /
    def GetCamStatusInfo(self,cid):
        # --/
        #
        #     Camera进程状态值
        #     0 -- Living
        #     1 -- WaitLiving Or Fault
        #     2 -- No Find Any Related Process
        #     3 -- Only Have FFmpeg Process
        #     4 -- Other Fault
        #
        # --/
        ptmp1 = subprocess.Popen("/bin/ps -aux | grep %s | grep -v grep | grep ffstart | wc -l"%cid,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        DaemonNum= int(ptmp1.stdout.read())
        ptmp2 = subprocess.Popen("/bin/ps -aux | grep %s | grep -v grep | grep ffmpeg | wc -l"%cid,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        FfmpegNum = int(ptmp2.stdout.read())
        if DaemonNum == 1 and FfmpegNum == 1:
            CamStatus = 0
        elif DaemonNum == 1 and FfmpegNum == 0:
            CamStatus = 1
        elif DaemonNum == 0 and FfmpegNum == 0:
            CamStatus = 2
        elif DaemonNum == 0 and FfmpegNum == 1:
            CamStatus = 3
        else:
            CamStatus = 4

        self.IsSendMail(CamStatus,cid)
        
        # --/
        #       
        #     Camera FFmpeg进程重启状况
        #     0 -- No Restart The Scan Interval
        #     1 -- Have Restart The Scan Interval
        #     2 -- No Exist The Camera FFmpeg Process For The Cid
        #
        # --/
        if CamStatus == 0 or CamStatus == 3:
            ptmp3 = subprocess.Popen("/bin/ps -aux | grep %s | grep -v grep | grep ffmpeg | awk '{print $2}'"%cid,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)    
            pid = ptmp3.stdout.read()
            if self.CidRestartTimePoint.has_key(cid):
                if self.CidRestartTimePoint[cid] == pid:
                    CamRestartStatus = 0
                else:
                    CamRestartStatus = 1
                    self.CidRestartTimePoint[cid] = pid
            else:
                CamRestartStatus = 0
                self.CidRestartTimePoint[cid] = pid
        else:
            CamRestartStatus = 2
                   
        return CamStatus,CamRestartStatus
    
    # -- / 
    #      依次扫描本服务器每一个Camera的状态
    # -- /
    def ScanCidsAndSendInfo(self):
        syslog.openlog("MonitorCamStatus")
        sock = socket.socket()
        try:
            sock.connect( (self.CARBON_SERVER,self.CARBON_PORT))
        except:
            syslog.syslog("Couldn't connect to %s on port %s"%(self.CARBON_SERVER,self.CARBON_PORT))
            sys.exit(1)
        while True:
            self.GetCidList()
            now = int(time.time())
            WaitSendInfo = []
            if len(self.CidList) != 0:
                for cid in self.CidList:
                    CamStatus,CamRestartStatus = self.GetCamStatusInfo(cid)
                    WaitSendInfo.append("%s.Camera.%s.CamStatus %s %d"%(self.ServerIPAddr,cid,CamStatus,now))
                    WaitSendInfo.append("%s.Camera.%s.CamRestartStatus %s %d"%(self.ServerIPAddr,cid,CamRestartStatus,now))
                message = '\n'.join(WaitSendInfo) + '\n'
                sock.sendall(message)
                time.sleep(self.delay)

    # --/
    #     主程序
    # --/
    def main(self):
        self.ScanCidsAndSendInfo()

######################################################################                        
if __name__ == "__main__":
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
    SendCamStaToMonServer().main()
    
