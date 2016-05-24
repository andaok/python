#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# ------------------------------------------------ /
# Purpose:
#       Zabbix Api Interface For Sender Camera Monitor Data To Zabbix
# @Author: wye
# @Date: 2015-10-22
# @Achieve basic functions
# ------------------------------------------------ /

import json 
import urllib2
import sys
import socket
import fcntl
import struct
import logging
import logging.handlers
from urllib2 import Request,urlopen,URLError,HTTPError


# ---------------------- /
#  GET SERVER IP ADDRESS
# ---------------------- /

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


# ---------------------- /
#  MAIN PROGRAM
# ---------------------- /

class ZabbixAPI(object):

    def __init__(self,cid,zabbix_server_info,logger):

        self.cid = cid
        self.zabbix_url = zabbix_server_info['zabbix_url']
        self.zabbix_user = zabbix_server_info['zabbix_user']
        self.zabbix_pass = zabbix_server_info['zabbix_pass']

        self.zabbix_header = {"Content-Type":"application/json"}
        self.HostGroupName = "Collect Stream Server"
        self.TemplateName = "Template OS Linux"

        self.NetCard = "br0"
        self.auth_code = None
        self.HostGroupId = None
        self.TemplateId = None
        self.HostId = None
        self.ItemId = None

        self.HostIPaddr = ifconfig(self.NetCard)
        self.HostName = "luxiang_" + self.HostIPaddr + "_vm"
        self.ItemName = "%s Online State"%self.cid
        self.keyName = "%s.OnlineState"%self.cid

 
        self.logger = logger


    def ReqToZabbix(self,request):
        try:
            result = urllib2.urlopen(request)
        except HTTPError,e:
            self.logger.error("the server couldn\'t fulfill the request,Error code:%s"%e.code)
        except URLError,e:
            self.logger.error("we failed to reach a server reason:%s"%e.reason)
        else:
            response = json.loads(result.read())
            result.close()
            return response

    
    def GetSessionId(self):
        auth_data = json.dumps(
             {
                 "jsonrpc":"2.0",
                 "method":"user.login",
                 "params":
                     {
                        "user":self.zabbix_user,
                        "password":self.zabbix_pass
                     },
                 "id":0  
             }
        )

        request = urllib2.Request(self.zabbix_url,auth_data)
        for key in self.zabbix_header:
            request.add_header(key,self.zabbix_header[key])
     
        response = self.ReqToZabbix(request)
        if 'result' in response: 
            self.auth_code = response['result']
        else:
            ErrorInfo = response['error']['data']
            self.logger.error("GetSessionId Error,Error Info : %s"%ErrorInfo)


    def GetHostGroupId(self):
        json_data = json.dumps(
             {
                 "jsonrpc":"2.0",
                 "method":"hostgroup.get",
                 "params":{
                             "output":"extend",
                             "filter":{"name":[self.HostGroupName]}                 
                },

                 "auth":self.auth_code,
                 "id":1     
             }
        )

        if self.auth_code == None:
            self.logger.error("SessionID Error")
        else:
            request = urllib2.Request(self.zabbix_url,json_data)
            for key in self.zabbix_header:
                request.add_header(key,self.zabbix_header[key])

            response = self.ReqToZabbix(request)
            if len(response['result']) == 0:
                self.logger.error("Did not find the specified hostgroup \'%s\',Please Create it manually"%self.HostGroupName)
            else:
                self.HostGroupId = response['result'][0]['groupid']

        
    def GetTemplateId(self):
        json_data = json.dumps(
             {
                  "jsonrpc":"2.0",
                  "method":"template.get",
                  "params":{
                              "output":"extend",
                              "filter":{"host":[self.TemplateName]}
                  },

                  "auth":self.auth_code,
                  "id":1  
             }
        )

        if self.auth_code == None:
            self.logger.error("SessionID Error")
        else:
            request = urllib2.Request(self.zabbix_url,json_data)
            for key in self.zabbix_header:
                request.add_header(key,self.zabbix_header[key])

            response = self.ReqToZabbix(request)
            if len(response['result']) == 0:
                self.logger.error("Did not find the specified template \'%s\',Please Create it manually"%self.TemplateName)
            else:
                self.TemplateId = response['result'][0]['templateid']
        

    def GetHostInfo(self,HostName):
        json_data = json.dumps(
             {
                   "jsonrpc":"2.0",
                   "method":"host.get",
                   "params":{
                                "output":"extend",
                                "filter":{"host":[HostName]} 
                   }, 

                   "auth":self.auth_code,
                   "id":1
             }

        )

        if self.auth_code == None:
            self.logger.error("SessionID Error")
        else:
            request = urllib2.Request(self.zabbix_url,json_data)
            for key in self.zabbix_header:
                request.add_header(key,self.zabbix_header[key])

            response = self.ReqToZabbix(request)
            if len(response['result']) == 0:
                return False
            else:
                self.HostId = response['result'][0]['hostid']
                return True


    def CreateHost(self,HostName,HostIPaddr):
        json_data = json.dumps(
            {
                     "jsonrpc":"2.0",
                     "method":"host.create",
                     "params":{
                                   "host":HostName,
                                   "interfaces":[
                                       {
                                           "type":1,
                                           "main":1,
                                           "useip":1,
                                           "ip":HostIPaddr,
                                           "dns":"",
                                           "port":"10050"
                                       }
                                   ],

                                   "groups":[{"groupid":self.HostGroupId}],
                                   "templates":[{"templateid":self.TemplateId}],
                                   "inventory":{"macaddress_a":"01234","macaddress_b":"56768"}
                     },

                     "auth":self.auth_code,
                     "id":1
            }
        )

        if self.auth_code == None:
            self.logger.error("SessionID Error")
        else:
            request = urllib2.Request(self.zabbix_url,json_data)
            for key in self.zabbix_header:
                request.add_header(key,self.zabbix_header[key])

            response = self.ReqToZabbix(request)
            if 'result' in response:
                self.logger.info("The host %s create success in zabbix!"%HostName)
                self.HostId = response['result']['hostids'][0]
            else:
                self.logger.error("The host %s create Failure in zabbix!"%HostName)   


    def GetItemInfo(self,ItemName):
        json_data = json.dumps(
              {
                     "jsonrpc":"2.0",
                     "method":"item.get",
                     "params":{
                         "output":"extend",
                         "hostids":self.HostId,
                         "filter":{"name":[ItemName]}   
                     },
                     "auth":self.auth_code,
                     "id":1    
              }
        )

        if self.auth_code == None:
            self.logger.error("SessionID Error")
        else:
            request = urllib2.Request(self.zabbix_url,json_data)
            for key in self.zabbix_header:
                request.add_header(key,self.zabbix_header[key])

            response = self.ReqToZabbix(request)
            if len(response['result']) == 0:
                return False
            else:
                return True


    def CreateItem(self,ItemName,keyName):
        json_data = json.dumps(
              {
                      "jsonrpc":"2.0",
                      "method":"item.create",
                      "params":{
                           "name":ItemName,
                           "key_":keyName,
                           "hostid":self.HostId,
                           "type":2,
                           "value_type":3,
                           "delay":30,
                           "history":30,
                           "trends":90
                      },

                      "auth":self.auth_code,
                      "id":1
              }
        )

        if self.auth_code == None:
            self.logger.error("SessionID Error")
        else:
            request = urllib2.Request(self.zabbix_url,json_data)
            for key in self.zabbix_header:
                request.add_header(key,self.zabbix_header[key])        
        
            response = self.ReqToZabbix(request)
            if 'result' in response:
                self.logger.info("The Item %s create succes in zabbix"%ItemName)
                self.ItemId = response['result']['itemids'][0]
            else:
                self.logger.error("The Item %s create Failure in zabbix!"%ItemName)   


    def SenderData(self):
        pass

    def IsExistHost(self):
        if self.GetHostInfo(self.HostName) == False:
            self.logger.error("Did not find the specified host \'%s\',System will be create it"%self.HostName)
            self.CreateHost(self.HostName,self.HostIPaddr)
        else:
            self.logger.info("The specified host \'%s\' is exist,Continue to execute other code ..."%self.HostName)

    
    def IsExistItem(self):
        if self.GetItemInfo(self.ItemName) == False:
            self.logger.error("Did not find the specified Item \'%s\',System will be create it"%self.ItemName)
            self.CreateItem(self.ItemName,self.keyName)
        else:
            self.logger.info("the specified Item \'%s\' is exist,Continue to execute other code ..."%self.ItemName)

        


if __name__ == "__main__":

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
    
    logger = GetLog("ZabbixAPI")   
    try: 
        zabbix_server_info = {"zabbix_url":"http://192.168.0.111/zabbix/api_jsonrpc.php","zabbix_user":"admin","zabbix_pass":"zabbix"}
        ZabbixAPIObj = ZabbixAPI("ZIKKKKK",zabbix_server_info,logger)
        ZabbixAPIObj.GetSessionId()
        ZabbixAPIObj.GetHostGroupId()
        ZabbixAPIObj.GetTemplateId()
        ZabbixAPIObj.IsExistHost()
        ZabbixAPIObj.IsExistItem()

        print ZabbixAPIObj.auth_code , ZabbixAPIObj.HostGroupId , ZabbixAPIObj.TemplateId
    except IndexError,e:
        logger.error("ZabbixAPI Exception,Error is %s,Main Program not quit,GOON..."%e)
    
    print "step 2"


        



    







