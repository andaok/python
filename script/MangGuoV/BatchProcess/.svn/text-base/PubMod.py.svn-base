#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Created on Jan 9, 2013

@author: wye

Copyright @ 2012 - 2013  Cloudiya Tech . Inc 

"""

import os
import sys
import xlwt
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
from email.header import Header
from email.mime.text import MIMEText
from WebHdfsAPI import WebHadoop

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
        
        self.MongodbIp = "10.2.10.10"        
        self.MongodbPort = 27017
        self.MongodbName = "video"
        
        self.MysqldbIp = "10.2.10.12"
        self.MysqldbPort = 3306
        self.MysqlUser = "cloudiya"
        self.MysqlPassword = "c10udiya"
        self.MysqlDbname = "video1"
        
        self.RedisIp = "10.2.10.19"
        self.RedisPort = 6379
        
        self.HdfsHost = "10.1.0.8,10.1.0.10"        
        self.HdfsPort = 14000
        self.HdfsUser = "cloudiyadatauser"
        self.HdfsPrefix="/webhdfs/v1"
        
        self.LogFile = "/tmp/BatchPro.log"
        self.LogLevel = "debug"
        self.LogFlag = "BatchPro"
        
        self.workers = 10
        
        #self.date = datetime.datetime.now().strftime("%Y%m%d")
        self.date = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%Y%m%d")
        #self.date = "20131224"

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


# --/
#     生成excel文件
# --/
def gen_excel_file(prefilename,savedir,labellist,rowlist):
    
    filename = prefilename + ".xls"
    
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet(filename)
    
    #Font Define
    font = xlwt.Font()
    font.name = "Times New Roman"
    font.bold = True
    font.colour_index = 2
    
    #Alignment Define
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_LEFT
    alignment.vert = xlwt.Alignment.VERT_BOTTOM
    
    #Borders Define
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    borders.left_colour = 0x40
    borders.right_colour = 0x40
    borders.top_colour = 0x40
    borders.bottom_colour = 0x40

    style = xlwt.XFStyle()
    style.font = font
    style.borders = borders 
    style.alignment = alignment
    
    #Write Label
    for colnum,colvalue in enumerate(labellist):
        sheet.write(0,colnum,colvalue,style)
        sheet.col(colnum).width = 6000
    
    #Write Data
    row = 1
    for rowdata in rowlist:
        for colnum,colvalue in enumerate(rowdata):
            sheet.write(row,colnum,colvalue,style)
        row += 1
        
    #Save Excel File 
    wbk.save("/tmp/%s"%filename)
    
    Config = HandleConfig()
    logger = getLog("Upload excel file to hdfs")
    HdfsObj = WebHadoop(Config.HdfsHost,Config.HdfsPort,Config.HdfsUser,logger,Config.HdfsPrefix)
    HdfsObj.put_file("/tmp/%s"%(filename), savedir+filename,overwrite="true")
    
    #Delete Tmp File
    os.remove("/tmp/%s"%(filename))

# --/
#     生成txt文件
# --/

def gen_txt_file(prefilename,savedir,labellist,rowlist):
    
    filename = prefilename + ".txt"
    labelstr = u"序号" + "," + ",".join(labellist)

    f = open("/tmp/%s"%filename,'wb')
    f.write(labelstr)
    f.write("\n")
    
    for rownum,rowvalue in enumerate(rowlist):
        rowdata = "%s"%(rownum+1)+","+",".join(rowvalue) 
        f.write(rowdata)
        f.write("\n")

    f.close()
    
    Config = HandleConfig()
    logger = getLog("Upload txt file to hdfs")
    HdfsObj = WebHadoop(Config.HdfsHost,Config.HdfsPort,Config.HdfsUser,logger,Config.HdfsPrefix)
    HdfsObj.put_file("/tmp/%s"%(filename), savedir+filename,overwrite="true")
    
    #Delete Tmp File
    os.remove("/tmp/%s"%(filename))
    

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


    Mail_list = {"server":"smtp.exmail.qq.com",
                 "fromAddr": "%s <support@skygrande.com>"%Header("天空视频网","utf-8"),
                 "user":"support@skygrande.com",
                 "passwd":"1qaz2wsx`"}
    
    MailSubjectDict = {}
    MailTextDict = {}
    
# -------------------------------
    '''邮件主题与正文'''
    '''免费用户当月流量超支导致服务中断'''
    FreeFlowOver_subject = u"服务中断通知！"
    FreeFlowOver_text = u'''尊敬的天空视频网用户：
                               到昨天为止，您使用的流量已经超过了本月流量上限，您本月的视频播放服务已经中断，请尽快充值流量或者考虑升级付费套餐的类型。

                               祝您使用愉快，如果您有任何意见或者建议，请随时联系我们的客服人员。
                       
                               电子邮箱：support@skygrande.com
                               电话：027-87204207
                         '''
    
    MailSubjectDict["FreeFlowOver"] = FreeFlowOver_subject
    MailTextDict["FreeFlowOver"] = FreeFlowOver_text
    
    '''免费用户流量报警'''
    FreeFlowAlert_subject = u"流量报警通知!"
    FreeFlowAlert_text = u'''尊敬的天空视频网用户：
                                到昨天为止，您使用的流量已经超过了本月流量上限的90%。为了防止您正常的视频播放受到影响，请尽快充值流量或者考虑升级付费套餐的类型。

                                温馨提示：为了更好的提供我们的视频服务，对于所有的付费套餐用户，如果您的流量已经超出本月流量上限且未能及时充值，我们将从您下个月的流量中借用不超过
                                         10%的流量来继续提供本月的视频播放服务。

                                祝您使用愉快，如果您有任何意见或者建议，请随时联系我们的客服人员。
                    
                                电子邮箱：support@skygrande.com
                                电话：027-87204207
                           '''
    
    MailSubjectDict["FreeFlowAlert"] = FreeFlowAlert_subject
    MailTextDict["FreeFlowAlert"] = FreeFlowAlert_text
    
    '''免费用户的充值流量报警'''
    RechargeFlowAlert_subject = u"充值流量报警通知"
    RechargeFlowAlert_text = u'''尊敬的天空视频网用户：
                                    到昨天为止，您使用的流量已经超过了充值流量的90%。为了防止您正常的视频播放受到影响，请尽快充值流量或者考虑升级购买我们的付费套餐。

                                    祝您使用愉快，如果您有任何意见或者建议，请随时联系我们的客服人员。
                     
                                    电子邮箱：support@skygrande.com
                                    电话：027-87204207
                              '''
    
    MailSubjectDict["RechargeFlowAlert"] = RechargeFlowAlert_subject
    MailTextDict["RechargeFlowAlert"] = RechargeFlowAlert_text

    '''免费用户的充值流量结束'''
    RechargeFlowOver_subject = u"充值流量结束通知"
    RechargeFlowOver_text = u'''尊敬的天空视频网用户：

                                   到昨天为止，您使用的流量已经超过了购买的充值流量。
                                   您将能够以永久免费的账户类型继续使用天空视频网提供的专业服务。我们提供的免费服务包括
                                  （1）上传不超过3个视频文件；
                                  （2）使用不超过1GB的存储空间使用；
                                  （3）每月赠送2GB的免费流量；

                                   祝您使用愉快，如果您有任何意见或者建议，请随时联系我们的客服人员。
                                 
                                   电子邮箱：support@skygrande.com
                                   电话：027-87204207
                             '''
    
    MailSubjectDict["RechargeFlowOver"] = RechargeFlowOver_subject
    MailTextDict["RechargeFlowOver"] = RechargeFlowOver_text

    '''免费用户充值流量到期'''
    RechargeFlowEnd_subject = u"充值流量到期通知"
    RechargeFlowEnd_text = u'''尊敬的天空视频网用户：
                                  到昨天为止，您充值流量的有效期已经结束。
                                  您将能够以永久免费的账户类型继续使用天空视频网提供的专业服务。我们提供的免费服务包括
                                 （1）上传不超过3个视频文件；
                                 （2）使用不超过1GB的存储空间使用；
                                 （3）每月赠送2GB的免费流量；

                                  祝您使用愉快，如果您有任何意见或者建议，请随时联系我们的客服人员。
                    
                                  电子邮箱：support@skygrande.com
                                  电话：027-87204207
                            '''

    MailSubjectDict["RechargeFlowEnd"] = RechargeFlowEnd_subject
    MailTextDict["RechargeFlowEnd"] = RechargeFlowEnd_text

    '''付费用户到期'''
    PayFlowEnd_subject = u"付费套餐结束通知"
    PayFlowEnd_text = u'''尊敬的天空视频网用户：
                             到昨天为止，您购买的付费套餐服务已经结束。由于您没有为本付费套餐续费，我们自动将您降级为免费用户。
                             您将能够以永久免费的账户类型继续使用天空视频网提供的专业服务。我们提供的免费服务包括
                            （1）上传不超过3个视频文件；
                            （2）使用不超过1GB的存储空间使用；
                            （3）每月赠送2GB的免费流量；

                             重要提示：如果您现在所有的视频文件所占用的存储空间超过1GB，我们将在7天后删除您的视频文件到占用存储空间不超过1GB为止。

                             祝您使用愉快，如果您有任何意见或者建议，请随时联系我们的客服人员。
                     
                             电子邮箱：support@skygrande.com
                             电话：027-87204207  
                      '''

    MailSubjectDict["PayFlowEnd"] = PayFlowEnd_subject
    MailTextDict["PayFlowEnd"] = PayFlowEnd_text

    '''付费用户的当月流量超过月限制流量90%'''
    PayFlowAlert_subject = u"流量报警通知"
    PayFlowAlert_text =  u'''尊敬的天空视频网用户：
                                到昨天为止，您使用的流量已经超过了本月流量上限的90%。为了防止您正常的视频播放受到影响，请尽快充值流量或者考虑升级付费套餐的类型。

                                温馨提示：为了更好的提供我们的视频服务，对于所有的付费套餐用户，如果您的流量已经超出本月流量上限且未能及时充值，我们将从您下个月的流量中借用不超过
                                        10%的流量来继续提供本月的视频播放服务。

                                祝您使用愉快，如果您有任何意见或者建议，请随时联系我们的客服人员。
                     
                                电子邮箱：support@skygrande.com
                                电话：027-87204207
                          '''
    
    MailSubjectDict["PayFlowAlert"] = PayFlowAlert_subject
    MailTextDict["PayFlowAlert"] = PayFlowAlert_text


    '''付费用户的当月流量超支导致服务中断'''
    PayFlowOver_subject = u"服务中断通知！"
    PayFlowOver_text = u'''尊敬的天空视频网用户：
                              到昨天为止，您使用的流量已经超过了本月流量上限，并且从下个月借用的流量也被全部使用。您本月的
                           视频播放服务已经中断，请尽快充值流量或者考虑升级付费套餐的类型。

                              祝您使用愉快，如果您有任何意见或者建议，请随时联系我们的客服人员。

                             电子邮箱：support@skygrande.com
                             电话：027-87204207
            '''
    
    MailSubjectDict["PayFlowOver"] = PayFlowOver_subject
    MailTextDict["PayFlowOver"] = PayFlowOver_text

# ------------------------------------------------------------
    
    msg = MIMEText(MailTextDict[mailflag],_charset="utf-8")
    msg["Subject"] = MailSubjectDict[mailflag]
    msg["From"] = Mail_list["fromAddr"]
    msg["To"] = mailaddr
    try:
        send_smtp = smtplib.SMTP()
        send_smtp.connect(Mail_list["server"])
        send_smtp.login(Mail_list["user"],Mail_list["passwd"])
        send_smtp.sendmail(Mail_list["fromAddr"],mailaddr,msg.as_string())
        send_smtp.close()
        return True
    except Exception,e:
        logger.error("Send mail to %s fail,Error info : %s "%(mailaddr,e))
        pass

if __name__ == "__main__":
    logger = getLog("tmptest")
    SendMail("wye@cloudiya.com","RechargeFlowEnd",logger)


