#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Created on Jan 9, 2013

@author: wye

Copyright @ 2012 - 2013  Cloudiya Tech . Inc 

"""

import sys
import redis
import ujson
import json
import time
import Queue
import threading
import datetime
import logging
import operator
import MySQLdb
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText

# --/
#     全局常量
# --/

class HandleConfig(object):
    
    def __init__(self):
        
        self.EX_CODE_1 = 101
        self.EX_CODE_2 = 102 
        self.EX_CODE_3 = 103
        self.EX_CODE_4 = 104
        self.EX_CODE_5 = 105
        
        self.MongodbIp = "192.168.0.203"        
        self.MongodbPort = 27017
        
        self.MysqldbIp = "192.168.0.112"
        self.MysqldbPort = 3306
        self.MysqlUser = "cloudiya"
        self.MysqlPassword = "c10udiya"
        self.MysqlDbname = "video"
        
        self.RedisIp = "192.168.0.111"
        self.RedisPort = 6379
        
        self.HdfsHost = "192.168.0.112"        
        self.HdfsPort = 50071
        self.HdfsUser = "cloudiyadatauser"
        self.HdfsPrefix="/webhdfs/v1"
        
        self.LogFile = "/tmp/BatchPro.log"
        self.LogLevel = "debug"
        self.LogFlag = "BatchPro"
        
        self.workers = 10
        
        #self.date = "20130610"
        #self.date = datetime.datetime.now().strftime("%Y%m%d")
        self.date = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%Y%m%d")


# --/
#     合并播放相同次数区段
# --/

def mergerPlaySeg(oldlist):
    newlist = []
    tmplist = []
    
    for k1,k2,v in oldlist:
        if len(tmplist) == 0:
            tmplist = [k1,k2,v]
        else:
            if tmplist[1] != k1:
                newlist.append(tmplist)
                tmplist = [k1,k2,v]
            else:
                if tmplist[2] != v:
                    newlist.append(tmplist)
                    tmplist = [k1,k2,v]
                else:
                    tmplist[1] = k2
    
    newlist.append(tmplist)
    
    return newlist


# --/
#     日志对象
# --/

def getLog(logflag,logfile="/tmp/BatchPro.log",loglevel="info"):
    
    logger = logging.Logger(logflag)
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter("%(asctime)s -- [ %(name)s ] -- %(levelname)s -- %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    
    if loglevel == "debug": 
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        
    return logger


# -- /
#      删除redis中临时数据
# -- /

def delTmpData(redata):
    keylist = redata.keys("T_*")
    
    redpipe = redata.pipeline()
    for key in keylist:
        redpipe.delete(key)
    redpipe.execute()
    
# -- /
#      获取月初日期列表
# -- /

def is_leap_year(year):
    if (year%4 == 0 and year%100 != 0) or year%400 == 0:
        return True
    else:
        return False
    
def get_days_list(date,num):
    month_list = {"1":31,"3":31,"4":30,"5":31,"6":30,"7":31,"8":31,"9":30,"10":31,"11":30,"0":31}
    
    if num == 0:num = 120
    
    date_list = str(date).split("-")
    year = date_list[0]
    month = date_list[1]
    day = date_list[2]
    
    year_num = num/12
    month_days = {}
    
    for i in range(num):
        month_num = int(month) + i
        if (month_num%12) !=2:
            month_days[str(month_num)] = month_list[str(month_num%12)]
        else:
            month_days[str(month_num)] = 28
            
    leap_year = []
    
    for i in range(year_num+2):
        if is_leap_year(int(year)+i):
            leap_year.append(29)
        else:
            leap_year.append(28)

    days_list = []
    sum = 0
    for i in month_days.iterkeys():
        if int(i)%12 == 2 :
            feb_days = int(i)/12
            month_days[i]= leap_year[feb_days]
            
    for i in month_days.iterkeys():
        sum += month_days[i]
        days_list.append(sum)

    new_days_list = days_list[:-1]
    new_days_list.append(0)
    begin_day_list = []
    
    for i in new_days_list:
        timeObj = time.strptime(date,'%Y-%m-%d')
        dateObj = datetime.datetime(*timeObj[:3])
        new_begin_day = (dateObj+datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        begin_day_list.append(new_begin_day)
    
    begin_day_list.remove(date)
   
    return begin_day_list

# --/
#      发邮件模块
# --/

def SendMail(mailaddr,mailflag,logger):
    
    Mail_list_tmp = {"server":"59.175.153.69",
                 "fromAddr": "support@cloudiya.com.com",
                 "user":"support@cloduiya.com",
                 "passwd":""}
    
    Mail_list = {"server":"stmp.exmail.qq.com",
                 "fromAddr": "support@skygrande.com",
                 "user":"support@skygrande.com",
                 "passwd":"1qaz2wsx`"}
    
    # -------------------------------
    '''邮件主题与正文'''
    '''降级'''
    FallLevel_subject = u"套餐降级通知！"
    FallLevel_text = u'''尊敬的天空视频网用户：
                     由于你购买的套餐或者充值流量已经到期，所以我们自动将您降级为免费用户，免费用户将有2GB/月的流量使用
                     和1GB的存储空间。如果您现在所有的视频文件所占用的存储空间超过1GB，我们将在7天后删除您的视频文件
                     到占用存储空间不超过1GB为止。

                     祝您使用愉快，如果您有什么建议或其他反馈请联系我们客服。
                     邮箱：support@skygrande.com.
                ''' 
    
    '''当月流量超过月限制流量90%'''
    MonthLimit90_subject = u"天空视频网 流量报警通知！"
    MonthLimit90_text =  u'''尊敬的天空视频网用户：
                     由于您本月使用的流量已经超过了购买的套餐月流量上限的90%，未防止你的视频播放中断，请尽快充值。
                     温馨提示：为了更好的提供我们的视频服务，对于所有的付费套餐用户，如果您未能及时充值，我们将
                     从您下个月的流量中借用10%来继续本月的流量使用。

                     祝您使用愉快，如果您有什么建议或其他反馈请联系我们客服。
                     邮箱：support@skygrande.com
            '''
    
    '''当月流量超过月限制流量'''
    MonthLimit_subject = u"天空视频网 流量超支通知！！！"
    MonthLimit_text = u'''尊敬的用户：
                     由于你购买的套餐流量已经超过了月流量，你的视频已经中断，请充值。
                     祝您使用愉快，如果您有什么建议或其他反馈请联系我们客服。
                     邮箱：support@skygrande.com
            '''
    
    MailSubjectDict = {"FallLevel":FallLevel_subject,"MonthLimit90":MonthLimit90_subject,"MonthLimit":MonthLimit_subject}
    MailTextDict = {"FallLevel":FallLevel_text,"MonthLimit90":MonthLimit90_text,"MonthLimit":MonthLimit_text}
    #--------------------------------
    
    msg = MIMEText(MailTextDict[mailflag],_charset="utf-8")
    msg["Subject"] = MailSubjectDict[mailflag]
    msg["From"] = Mail_list["fromAddr"]
    msg["To"] = mailaddr
    try:
        send_smtp = smtplib.SMTP()
        send_smtp.connect(Mail_list["server"])
        send_smtp.sendmail(Mail_list["fromAddr"],mailaddr,msg.as_string())
        send_smtp.close()
        return True
    except Exception,e:
        logger.error("Send mail to %s fail,Error info : %s "%(mailaddr,e))
        pass
