#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os
import sys
import smtplib
import threading
from email.header import Header
from email.mime.text import MIMEText




class SendMail(threading.Thread):
    def __init__(self,tomailaddr,subject,text):
 
        self.subject = subject
        self.text = text
        
        self.FromAddr = "support@skygrande.com"
        self.SmtpServer = "smtp.exmail.qq.com"
        self.user = "support@skygrande.com"
        self.pwd = "1qaz2wsx`"
        self.ToAddr = tomailaddr
        self.MailFlag = "Cloudiya Monitor Alert"
        
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
            print("Send mail to %s fail,Error info : %s "%(self.ToAddr,e))




if __name__ == "__main__":

    tomailaddr = sys.argv[1]
    subject = sys.argv[2]
    text = sys.argv[3]

    SendMailObj = SendMail(tomailaddr,subject,text)
    SendMailObj.start()
