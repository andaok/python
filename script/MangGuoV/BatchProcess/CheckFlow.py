#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
import datetime
import redis
import MySQLdb
import Queue
import threading
from pymongo import MongoClient
from UserInfo import UidInfo
from UserInfo import TypeInfo
import smtplib
from email.mime.text import MIMEText 


from PubMod import getLog
from PubMod import SendMail
from PubMod import HandleConfig
from PubMod import get_days_list


# --/
#     检查用户套餐状态,依情况作出相应处理.
# --/

class CheckUserPackage():
    
    def __init__(self,uid,logger,datadate,redata,mongoconn,mysql_conn):
        
        self.uid = uid
        self.logger = logger
        self.today = str(datadate)
        self.redata = redata
        self.mongoconn = mongoconn
        self.mysql_conn = mysql_conn
        
    def UserPackageInfo(self):
        
        self.UidObj = UidInfo(self.mysql_conn,self.mongoconn,self.uid)
        
        flow_info = self.UidObj.get_flow_info(self.uid)
        
        '''用户套餐所属类别ID'''
        self.Now_TypeID = flow_info[7]
        
        '''用户email地址'''
        self.Email = flow_info[8]
        
        '''用户套餐开始日期'''
        self.Now_StartDate = str(flow_info[0])
        '''用户套餐结束日期'''
        self.Now_EndDate = str(flow_info[1])
        
        '''用户套餐购买月数'''
        self.Now_Month_Count = flow_info[2]
        '''用户套餐月规定流量'''
        self.Now_Month_Flow = flow_info[3]
        '''用户该月已用流量'''
        self.Now_Month_Used_Flow = flow_info[4]
        '''用户该月已超流量'''
        self.Now_Month_Advance_Flow = flow_info[5]
        
        '''用户今天消耗流量'''
        self.Daily_Flow = self.UidObj.get_daily_flow(self.uid)/1024
        
        '''截至今天用户该月消耗总流量'''
        self.Month_Sum_Flow = self.Now_Month_Used_Flow + self.Now_Month_Advance_Flow + self.Daily_Flow
        
        '''Write to log file for debug'''
        self.logger.debug("Now Package info :      \n \
                           Uid : %s                \n \
                           TypeID : %s             \n \
                           Email  : %s             \n \
                           StartDate : %s          \n \
                           EndDate : %s            \n \
                           Month_Count : %s        \n \
                           Month_Flow : %s         \n \
                           Month_Used_Flow : %s    \n \
                           Month_Advance_Flow : %s \n \
                           Daily_Flow : %s         \n \
                           Month_Sum_Flow : %s     \n \
                         "%(self.uid,self.Now_TypeID,self.Email,self.Now_StartDate,self.Now_EndDate,self.Now_Month_Count,self.Now_Month_Flow,self.Now_Month_Used_Flow,self.Now_Month_Advance_Flow,self.Daily_Flow,self.Month_Sum_Flow))
        
    def FreeUserPackageInfo(self):
        
        '''免费套餐用户所属类别ID'''
        self.Free_TypeID = 2
        
        self.typeObj = TypeInfo(self.mysql_conn,self.Free_TypeID)
        
        '''免费套餐月规定流量'''
        self.Free_Month_Flow = self.typeObj.flow
        
        '''免费套餐结束日期'''
        self.Free_EndDate = "0000-00-00"
        
        '''免费套餐规定月数'''
        self.Free_Month_Count = 0
    
        '''Write to log file for debug'''
        self.logger.debug("Free Package info : \n \
                           Uid  : %s           \n \
                           TypeID : %s         \n \
                           Month_Flow : %s     \n \
                         "%(self.uid,self.Free_TypeID,self.Free_Month_Flow))
    
    def UserPackageExtInfo(self):
        
        Ext_TypeInfo = self.typeObj.get_ext_typeinfo(self.uid)
        
        '''扩展表开始时间'''
        self.old_starttime = str(Ext_TypeInfo[0])
        '''扩展表结束时间'''
        self.ext_enddate = str(Ext_TypeInfo[1])
        '''扩展表月流量限制'''
        self.o_mount_flow = Ext_TypeInfo[2]
        '''扩展表续费标签'''
        self.is_ext = Ext_TypeInfo[3]
        '''扩展表月数'''
        self.total_mouth = Ext_TypeInfo[4]
        
        '''Write to log file for debug'''
        self.logger.debug("Ext Package info : \n \
                           Uid : %s           \n \
                           old_starttime : %s \n \
                           ext_enddate : %s   \n \
                           o_mount_flow : %s  \n \
                           is_ext : %s        \n \
                           total_mouth : %s   \n \
                         "%(self.uid,self.old_starttime,self.ext_enddate,self.o_mount_flow,self.is_ext,self.total_mouth))
        
    def ExeMysqlCmd(self,sql,param):
        '''执行mysql语句'''
        SqlCmd = sql%param
        try:
            cursor = self.mysql_conn.cursor()
            self.mysql_conn.select_db('video')
            cursor.execute(sql,param)
            self.mysql_conn.commit()
        except Exception,e:
            self.logger.error("Execute sql error : \n %s "%SqlCmd)
        finally:
            self.logger.debug("Execute sql : \n  %s"%SqlCmd)
            
    def ExeRedisCmd(self,key,value):
        '''执行redis语句'''
        try:
            self.redata.set(key,value)
        except Exception,e:
            self.logger.error("Execute redis cmd error")
            
    
    def FallLevel(self,emailflag):
        '''用户套餐降级到免费套餐'''
        new_begindate = datetime.datetime.now().strftime("%Y-%m-%d")
        new_enddate = self.Free_EndDate
        new_month_flow = self.Free_Month_Flow
        new_month_count = self.Free_Month_Count
        now_month_used = self.Month_Sum_Flow - self.Now_Month_Flow
        if now_month_used >= 0:
            now_month_extr = now_month_used - self.Free_Month_Flow
            if now_month_extr > 0:
                new_month_used_flow = self.Free_Month_Flow
                new_month_advance_flow = now_month_extr
                is_flow_alarm = 1
                is_write_redis = 0
                
            elif now_month_extr < -self.Free_Month_Flow*0.1:
                new_month_used_flow = now_month_used
                new_month_advance_flow = 0
                is_flow_alarm = 0
                is_write_redis = 1
                 
            else:
                new_month_used_flow = now_month_used
                new_month_advance_flow = 0
                is_flow_alarm = 1
                is_write_redis = 1
        else:
            new_month_used_flow = 0
            new_month_advance_flow = 0
            is_flow_alarm = 0
            is_write_redis = 1
            
        data = [new_begindate,new_enddate,new_month_count,new_month_flow,new_month_used_flow,new_month_advance_flow,is_flow_alarm,is_write_redis]
        
        '''更新uflow表相关信息'''
        sqlOne = "update uflow set startdate=%s,enddate=%s,month_count=%s,month_flow=%s,month_used_flow=%s,month_advance_flow=%s,is_flow_alarm=%s where uid = %s"
        param = (data[0],data[1],data[2],data[3],data[4],data[5],data[6],self.uid)
        self.ExeMysqlCmd(sqlOne,param)
        
        
        '''更新uinfo表相关信息'''
        sqlTwo = "update uinfo set tid = %s where uid = %s"
        param = (self.Free_TypeID,self.uid)
        self.ExeMysqlCmd(sqlTwo,param)
        
        '''更新redis键uid_flow信息'''
        self.ExeRedisCmd("%s_flow"%self.uid,data[7])
        
        '''发邮件通知用户已降级'''
        SendMail(self.Email,emailflag,self.logger)


    def ContinueToPay(self):
        '''用户套餐续费'''
        old_starttime_list = self.old_starttime.split("-")
        old_endtime_list = self.Now_EndDate.split('-')
        old_starttime_list[0] = str(old_endtime_list[0])
        new_begindate = '-'.join(old_starttime_list)
        new_enddate = self.ext_enddate
        new_month_count = self.total_mouth - self.Now_Month_Count
        new_month_flow = self.o_mount_flow
        
        now_month_used = self.Month_Sum_Flow - self.Now_Month_Flow
        if now_month_used > 0:
            now_month_extr = now_month_used - new_month_flow
            if now_month_extr > new_month_flow*0.1:
                '''now_month_used > new_month_flow*110%'''
                new_month_used_flow = new_month_flow
                new_month_advance_flow = now_month_extr
                is_flow_alarm = 1
                is_write_redis = 0 
                SendMail(self.Email,"PayFlowOver",self.logger)               
            elif 0< now_month_extr <= new_month_flow*0.1:
                '''new_month_flow < now_month_used <= new_month_flow*110%'''
                new_month_used_flow = new_month_flow
                new_month_advance_flow = now_month_extr
                is_flow_alarm = 1
                is_write_redis = 1 
                SendMail(self.Email,"PayFlowAlert",self.logger)               
            elif -new_month_flow*0.1 < now_month_extr <=0 :
                '''new_month_flow*90% < now_month_used <= new_month_flow'''
                new_month_used_flow = now_month_used
                new_month_advance_flow = 0
                is_flow_alarm = 1
                is_write_redis = 1
                SendMail(self.Email,"PayFlowAlert",self.logger)  
            else:
                '''now_month_used < new_month_flow*90%'''
                new_month_used_flow = now_month_used
                new_month_advance_flow = 0
                is_flow_alarm = 0
                is_write_redis = 1                
        else:
            '''now_month_used <= 0'''
            new_month_used_flow = 0
            new_month_advance_flow = 0
            is_flow_alarm = 0
            is_write_redis = 1
        
        '''更新uflow相关信息'''
        sqlone = "update uflow set startdate=%s,enddate=%s,month_count=%s,month_flow=%s,month_used_flow=%s,month_advance_flow=%s,is_flow_alarm=%s where uid =%s"    
        param = (new_begindate,new_enddate,new_month_count,new_month_flow,new_month_used_flow,new_month_advance_flow,is_flow_alarm,self.uid)
        self.ExeMysqlCmd(sqlone,param)
        
        '''更新redis键uid_flow信息'''        
        self.ExeRedisCmd("%s_flow"%self.uid,is_write_redis)
                        
        '''更新ucurrntetc表，开启续费开关'''
        sqltwo = 'update ucurrenttc set xufei_status=1 where uid = %s' 
        param = (uid)
        self.ExeMysqlCmd(sqltwo,param)


    def FreePackageInMonthMiddle(self):
        '''免费套餐在月中'''
        now_month_used = self.Month_Sum_Flow - self.Now_Month_Flow
        if now_month_used >= 0:
            new_month_used_flow = self.Now_Month_Flow
            new_month_advance_flow = now_month_used
            is_flow_alarm = 1
            is_write_redis = 0
            SendMail(self.Email,"FreeFlowOver",self.logger)
        elif now_month_used < -self.Now_Month_Flow*0.1:
            new_month_used_flow = self.Month_Sum_Flow
            new_month_advance_flow = 0
            is_flow_alarm = 0
            is_write_redis = 1
        else:
            new_month_used_flow = self.Month_Sum_Flow
            new_month_advance_flow = 0
            is_flow_alarm = 1
            is_write_redis = 1  
            SendMail(self.Email,"FreeFlowAlert",self.logger)     
            
        '''更新uflow相关信息'''    
        sql = "update uflow set month_used_flow=%s,month_advance_flow=%s,is_flow_alarm=%s where uid =%s"
        param = (new_month_used_flow,new_month_advance_flow,is_flow_alarm,self.uid)
        self.ExeMysqlCmd(sql,param)
        
        '''更新redis键uid_flow信息'''        
        self.ExeRedisCmd("%s_flow"%self.uid,is_write_redis)    
    
    def RechargePackageInMonthMiddle(self):
        '''充值套餐在月中'''
        now_month_used = self.Month_Sum_Flow - self.Now_Month_Flow
        if now_month_used >= 0:
            '''充值流量全部用完,降级'''
            self.FallLevel("RechargeFlowOver")          
        else:
            if self.Month_Sum_Flow > self.Now_Month_Flow*0.9 :
                new_month_used_flow = self.Month_Sum_Flow
                new_month_advance_flow = 0
                is_flow_alarm = 1
                is_write_redis = 1
                SendMail(self.Email,"RechargeFlowAlert",self.logger)
            else:
                new_month_used_flow = self.Month_Sum_Flow
                new_month_advance_flow = 0
                is_flow_alarm = 0
                is_write_redis = 1
            
            '''更新uflow相关信息''' 
            sql = "update uflow set month_used_flow=%s,month_advance_flow=%s,is_flow_alarm=%s where uid =%s"
            param = (new_month_used_flow,new_month_advance_flow,is_flow_alarm,self.uid)
            self.ExeMysqlCmd(sql,param)

            '''更新redis键uid_flow信息'''        
            self.ExeRedisCmd("%s_flow"%self.uid,is_write_redis)   


    def PayPackageInMonthMiddle(self):
        '''付费套餐在月中'''
        now_month_used = self.Month_Sum_Flow - self.Now_Month_Flow
        if now_month_used > self.Now_Month_Flow*0.1:
            '''self.Month_Sum_Flow > self.Now_Month_Flow*110%'''
            new_month_used_flow = self.Now_Month_Flow
            new_month_advance_flow = now_month_used
            is_flow_alarm = 1
            is_write_redis = 0
            SendMail(self.Email,"PayFlowOver",self.logger)       
        elif 0 < now_month_used <= self.Now_Month_Flow*0.1:
            '''self.Now_Month_Flow < self.Month_Sum_Flow <= self.Now_Month_Flow*110%'''
            new_month_used_flow = self.Now_Month_Flow
            new_month_advance_flow = now_month_used
            is_flow_alarm = 1
            is_write_redis = 1
            SendMail(self.Email,"PayFlowAlert",self.logger)
        elif -self.Now_Month_Flow*0.1 < now_month_used <=0:
            '''self.Now_Month_Flow*90% < self.Month_Sum_Flow <= self.Now_Month_Flow'''
            new_month_used_flow = self.Month_Sum_Flow
            new_month_advance_flow = 0
            is_flow_alarm = 1
            is_write_redis = 1
            SendMail(self.Email,"PayFlowAlert",self.logger)
        else:
            '''self.Month_Sum_Flow < self.Now_Month_Flow*90%'''
            new_month_used_flow = self.Month_Sum_Flow
            new_month_advance_flow = 0
            is_flow_alarm = 0
            is_write_redis = 1      
        
        '''更新uflow相关信息''' 
        sql = "update uflow set month_used_flow=%s,month_advance_flow=%s,is_flow_alarm=%s where uid =%s"         
        param = (new_month_used_flow,new_month_advance_flow,is_flow_alarm,self.uid)
        self.ExeMysqlCmd(sql,param)

        '''更新redis键uid_flow信息'''        
        self.ExeRedisCmd("%s_flow"%self.uid,is_write_redis)   
           
    def FreePackageInMonthFirst(self):
        '''免费套餐在月初'''
        now_month_used = self.Month_Sum_Flow - self.Now_Month_Flow
        now_month_extr = now_month_used - self.Now_Month_Flow 
        if now_month_used >= 0:
            if now_month_extr >= 0:
                new_month_used_flow = self.Now_Month_Flow 
                new_month_advance_flow = now_month_extr
                is_flow_alarm = 1
                is_write_redis = 0
                SendMail(self.Email,"FreeFlowOver",self.logger)
            elif now_month_extr < -self.Now_Month_Flow*0.1:
                new_month_used_flow = now_month_used
                new_month_advance_flow = 0
                is_flow_alarm = 0
                is_write_redis = 1
            else:
                new_month_used_flow = now_month_used
                new_month_advance_flow = 0
                is_flow_alarm = 1
                is_write_redis = 1
                SendMail(self.Email,"FreeFlowAlert",self.logger)
        else:
            new_month_used_flow = 0
            new_month_advance_flow = 0
            is_flow_alarm = 0
            is_write_redis =1                
        
        '''更新uflow相关信息'''
        sql = "update uflow set month_used_flow=%s,month_advance_flow=%s,is_flow_alarm=%s where uid = %s "
        param = (new_month_used_flow,new_month_advance_flow,is_flow_alarm,self.uid)
        self.ExeMysqlCmd(sql,param)

        '''更新redis键uid_flow信息'''        
        self.ExeRedisCmd("%s_flow"%self.uid,is_write_redis)
        
    def RechargePackageInMonthFirst(self):
        '''充值套餐在月初'''
        now_month_used = self.Month_Sum_Flow - self.Now_Month_Flow
               
        if now_month_used >= 0:
            '''充值流量用完,降级'''
            self.FallLevel("RechargeFlowOver")
        else:
            new_month_flow = self.Now_Month_Flow - self.Month_Sum_Flow 
            new_month_used_flow = 0
            new_month_advance_flow = 0
            is_flow_alarm = 0
            is_write_redis = 1
            if self.Month_Sum_Flow >= self.Now_Month_Flow*0.9:
                is_flow_alarm = 1
                SendMail(self.Email,"RechargeFlowAlert",self.logger)
                
            '''更新uflow相关信息'''
            sql = "update uflow set month_flow=%s,month_used_flow=%s,month_advance_flow=%s,is_flow_alarm=%s where uid =%s"    
            param = (new_month_flow,new_month_used_flow,new_month_advance_flow,is_flow_alarm,self.uid)
            self.ExeMysqlCmd(sql,param)
            
            '''更新redis键uid_flow信息'''        
            self.ExeRedisCmd("%s_flow"%self.uid,is_write_redis)
                                                                   
    def PayPackageInMonthFirst(self):
        '''付费套餐到月初'''
        now_month_used = self.Month_Sum_Flow - self.Now_Month_Flow
        if now_month_used > 0:
            now_month_extr = now_month_used  - self.Now_Month_Flow
            if now_month_extr > self.Now_Month_Flow*0.1:
                '''now_month_used > self.Now_Month_Flow*110%'''
                new_month_used_flow = self.Now_Month_Flow
                new_month_advance_flow = now_month_extr
                is_flow_alarm = 1
                is_write_redis = 0 
                SendMail(self.Email,"PayFlowOver",self.logger)            
            elif 0< now_month_extr <= self.Now_Month_Flow*0.1:
                '''self.Now_Month_Flow < now_month_used <= self.Now_Month_Flow*110% '''
                new_month_used_flow = self.Now_Month_Flow
                new_month_advance_flow = now_month_extr
                is_flow_alarm = 1
                is_write_redis = 1 
                SendMail(self.Email,"PayFlowAlert",self.logger)              
            elif -self.Now_Month_Flow*0.1 < now_month_extr <=0:
                '''self.Now_Month_Flow*90% < now_month_used <= self.Now_Month_Flow '''
                new_month_used_flow = now_month_used
                new_month_advance_flow = 0
                is_flow_alarm = 1
                is_write_redis = 1
                SendMail(self.Email,"PayFlowAlert",self.logger)  
            else:
                new_month_used_flow = now_month_used
                new_month_advance_flow = 0
                is_flow_alarm = 0
                is_write_redis = 1                
        else: 
            new_month_used_flow = 0
            new_month_advance_flow = 0
            is_flow_alarm = 0
            is_write_redis = 1
        
        '''更新uflow相关信息'''    
        sql = "update uflow set month_used_flow=%s,month_advance_flow=%s,is_flow_alarm=%s where uid =%s"
        param = (new_month_used_flow,new_month_advance_flow,is_flow_alarm,self.uid)
        self.ExeMysqlCmd(sql,param)
 
        '''更新redis键uid_flow信息'''        
        self.ExeRedisCmd("%s_flow"%self.uid,is_write_redis)
    
    def MainHandle(self):
        
        '''用户套餐信息'''
        self.UserPackageInfo()
        '''免费套餐信息'''
        self.FreeUserPackageInfo()
        '''用户月初日期列表'''
        BeginDate_List =  get_days_list(self.Now_StartDate,self.Now_Month_Count)
        
        
        # ----------------------------------
        # 付费套餐用户套餐到期,分两种情况：
        #    如有套餐续费,继续该用户购买的原始套餐
        #    如无套餐续费,降级到免费用户
        # 充值套餐用户套餐到期,分两种情况：
        #    如有套餐续费,继续该用户购买的原始套餐
        #    如无套餐续费,降级到免费用户
        # ----------------------------------
        if self.today == self.Now_EndDate:
            self.logger.debug("user %s handle step is in enddate"%self.uid)
            if self.Now_TypeID == self.Free_TypeID:
                '''充值套餐到期，降级'''
                self.FallLevel("RechargeFlowEnd")
            else:
                self.UserPackageExtInfo()
                if self.is_ext == 1:
                    '''套餐不续费,降级'''
                    self.FallLevel("PayFlowEnd")
                else:
                    '''套餐续费'''
                    self.ContinueToPay()
                
        
        # ---------------------------------
        # 付费套餐用户,充值用户,免费套餐用户到月初
        #----------------------------------
        if self.today in BeginDate_List:
            self.logger.debug("user %s handle step is month first"%self.uid)
            if self.Now_TypeID == self.Free_TypeID and self.Now_Month_Count == 0:
                '''免费套餐到月初'''
                self.FreePackageInMonthFirst()
            elif self.Now_TypeID == self.Free_TypeID and self.Now_Month_Count != 0:
                '''充值套餐到月初'''
                self.RechargePackageInMonthFirst()
            else:
                '''付费套餐到月初'''
                self.PayPackageInMonthFirst()
                
                
        # ---------------------------------
        # 付费套餐用户,充值用户,免费套餐用户在月中
        # ---------------------------------    
        if self.today not in BeginDate_List:
            self.logger.debug("user %s handle step is month middle"%self.uid)
            if self.Now_TypeID == self.Free_TypeID and self.Now_Month_Count == 0:
                '''免费套餐在月中'''
                self.FreePackageInMonthMiddle()
            elif self.Now_TypeID == self.Free_TypeID and self.Now_Month_Count != 0:
                '''充值套餐在月中,注：充值套餐用户TypeID和免费套餐用户TypeID一样'''
                self.RechargePackageInMonthMiddle()
            else:
                '''付费套餐在月中'''
                self.PayPackageInMonthMiddle()
                
        

try:
    Config = HandleConfig()

    logger = getLog("Step8",logfile=Config.LogFile,loglevel=Config.LogLevel)
    
    logger.info("Step8 Handle Start")
    
    datadate = Config.date

    redispool = redis.ConnectionPool(host=Config.RedisIp,port=6379,db=0)
    redata = redis.Redis(connection_pool=redispool)    
    
    mongoconn = MongoClient(Config.MongodbIp,27017)
    
    mysql_conn = MySQLdb.connect(host=Config.MysqldbIp,user=Config.MysqlUser,port=Config.MysqldbPort,passwd=Config.MysqlPassword,db=Config.MysqlDbname,charset="utf8")
        
    # ----
    set_alluser = redata.smembers("user_info")
    if redata.exists("CheckFlow_User"):
        checked_user = redata.smembers("CheckFlow_User")
        set_user = set_alluser - checked_user
        list_user = list(set_user)
    else:
        list_user = list(set_alluser)
       
    for i in list_user:
        CheckObj = CheckUserPackage(i,logger,datadate,redata,mongoconn,mysql_conn)
        CheckObj.MainHandle()
        redata.sadd("CheckFlow_User",i)
   
    if len(redata.smembers("CheckFlow_User")) == len(set_alluser):
        logger.info("Step8 Handle End")
        redata.delete("CheckFlow_User")
    else:
        logger.error("Step8 Handel error,please run it again!!!!")
    # ----
    
except Exception,e:
    logger.error(e)
    sys.exit(Config.EX_CODE_2)
    
    