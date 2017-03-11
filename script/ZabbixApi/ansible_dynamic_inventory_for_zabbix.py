#!/usr/bin/env python
# -*- encoding:utf-8 -*-

#------------------------------------------
# @Date    : 2017-03-11 16:41:17
# @Author  : wye
# @Version : v1.0
# @Descr   : ansible dynamic inventory for zabbix
# -----------------------------------------

import json
import urllib2
import sys
from urllib2 import Request,urlopen,URLError,HTTPError

# zabbix_url = "http://172.29.19.73/zabbix/api_jsonrpc.php"
# zabbix_header = {"Content-Type":"application/json"}
# zabbix_user = "admin"
# zabbix_pass = "zabbix"
# auth_code = ""

zabbix_url = "http://172.16.250.50/zabbix/api_jsonrpc.php"
zabbix_header = {"Content-Type":"application/json"}
zabbix_user = ""
zabbix_pass = ""
auth_code = ""

def login_zabbix():
    global auth_code
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


def call_zabbix_api(json_data):

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

        return response


def get_all_groups_info():

    json_data = {
        "method":"hostgroup.get",
        "params":{
               "output":"extend"
        }
    }   

    res = call_zabbix_api(json_data)

    groups_list = [ i['groupid']+"|"+i['name'] for i in res['result']]

    return groups_list


def get_all_hosts_info_in_group(groupid):

    json_data = {
            "method":"host.get",
            "params":{
                   "output":"extend",
                   "templateids":10294,
                   "groupids":groupid
            }
    }


    res = call_zabbix_api(json_data)

    hostsname_list = [ i['name'] for i in res['result']]

    return hostsname_list

# -------------------------------

import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="zabbix inventory script")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list',action='store_true')
    group.add_argument('--host')
    return parser.parse_args()


if __name__ == "__main__":

    login_zabbix()
    groups_list = get_all_groups_info()

    hosts = {}

    for i in groups_list:
        groupid = i.split("|")[0]
        groupname = i.split("|")[1]
        hostname_list = get_all_hosts_info_in_group(groupid)
        hosts[groupname] = hostname_list


    hosts["_meta"] = {
                       "hostvars":{
                                   "172.28.32.86":{"approle":"hadoopslave"},
                                   "172.28.32.82":{"approle":"hadoopmaster"}
                       }
                     }

    args = parse_args()

    if args.list:
        print json.dumps(hosts)
    else:
        print None

