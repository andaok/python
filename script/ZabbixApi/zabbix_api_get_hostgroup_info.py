#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import json 
import urllib2
import sys
from urllib2 import Request,urlopen,URLError,HTTPError

zabbix_url = "http://192.168.0.111/zabbix/api_jsonrpc.php"
zabbix_header = {"Content-Type":"application/json"}
zabbix_user = "admin"
zabbix_pass = "zabbix"
auth_code = ""

auth_data = json.dumps(
    {
            "jsonrpc":"2.0",
            "method":"user.login",
            "params":
                   {
                        "user":zabbix_user,
                        "password":zabbix_pass
                   },
            "id":0  
    }
    )

request = urllib2.Request(zabbix_url,auth_data)
for key in zabbix_header:
    request.add_header(key,zabbix_header[key])


try:
    result = urllib2.urlopen(request)
except HTTPError,e:
    print "the server couldn\'t fulfill the request,Error code:",e.code
except URLError,e:
    print "we failed to reach a server reason:",e.reason
else:
    response = json.loads(result.read())
    result.close()

    if 'result' in response: 
        auth_code = response['result']
    else:
        print response['error']['data']



json_data = {
    "method":"hostgroup.get",
    "params":{
           "output":"extend",
           "filter":{
               "name":[
                   "Cloudiya Tech Company12"
               ]
           } 
    }
}

json_base = {
    "jsonrpc":"2.0",
    "auth":auth_code,
    "id":1
}

json_data.update(json_base)

if len(auth_code) == 0:
    sys.exit(1)
if len(auth_code) != 0:
    get_host_data = json.dumps(json_data)
    request = urllib2.Request(zabbix_url,get_host_data)
    for key in zabbix_header:
        request.add_header(key,zabbix_header[key])



try:
    result = urllib2.urlopen(request)
except URLError as e:
    if hasattr(e,'reason'):
        print "we failed to reach a server"
        print "reason:",e.reason
    elif hasattr(e,'code'):
        print "the server could not fulfill the request"
        print "Error code:",e.code
else:
    response = json.loads(result.read())
    result.close()


    print response
    print "Group ID IS :" , response['result'][0]['groupid']



















