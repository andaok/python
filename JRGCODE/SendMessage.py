#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# -----------------------------------------
# Purpose:
#     Call SMS platform interface to send zabbix alarm message
# ------------------------------------------
# @Author : weiye
# @Date : 2016-06-16
# @Complete basic functions
# -----------------------------------------

import sys
import json
import urllib
import httplib

besType = "007"
deptType = "005"

HttpTimeout = 1

ApiInterServer = "172.16.4.57"
ApiInterPort = 80
ApiInterURL = "/sms-frontal/MessageController/sendMsg"

def SendMessage(phoneNumber,content,deptType,besType):
    httpClient = None
    try:
        params = urllib.urlencode({"phoneNumber":phoneNumber,"content":content,"deptType":deptType,"besType":besType})
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        httpClient = httplib.HTTPConnection(ApiInterServer,ApiInterPort,timeout=HttpTimeout)
        httpClient.request('POST', ApiInterURL,params,headers)
        response = httpClient.getresponse()
        print response.status , response.read()
    except Exception,e:
        print ("Error Info : %s"%e)
    finally:
        if httpClient:
            httpClient.close()

if __name__ == "__main__":

    phoneNumber = sys.argv[1]
    subject = sys.argv[2]
    text = sys.argv[3]
    SendMessage(phoneNumber,text,deptType,besType)
