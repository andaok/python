#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# -----------------------------------
# @Date     :  2017-08-21 12:48:00
# @Author   :  wye
# @Version  :  v1.0
# @Descr    :  monitor for elasticsearch
# ----------------------------------

"""
Zabbix monitor for elasticsearch
"""

# ------------------------

import os
import sys
import json
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError

# ------------------------

ELASTICSEARCH_HOST = "127.0.0.1"
ELASTICSEARCH_PORT = 9200

# ------------------------

def CallApiGetData(url):
    """
    Call api interface get data
    """
    
    request = urllib2.Request(url)
    try:
        result = urllib2.urlopen(request)
    except HTTPError,e:
        return False, "the server could\'t fulfill the requset, Error code:%s"%e.code
    except URLError,e:
        return False, "failed to reach a server reason:%s"%e.reason
    else:
        RunDataDict = json.loads(result.read())
        return True, RunDataDict


class ExecFunByZabbixRequest(object):
    def __init__(self,paras):
        self.ELASTICSEARCH_HOST = ELASTICSEARCH_HOST
        self.ELASTICSEARCH_PORT = ELASTICSEARCH_PORT
        try:
            fun_obj = getattr(self,paras[0])
        except AttributeError:
            print "Don't find this func %s"%paras[0]
        else:
            fun_obj(paras[1:])

    def es_cluster_status_metrics(self,paras):
        url = "http://%s:%s/_cluster/health"%(self.ELASTICSEARCH_HOST,self.ELASTICSEARCH_PORT)
        result_flag,stats_data = CallApiGetData(url)
        metrics_name = paras[0]
        
        if metrics_name == "cluster_status":
            if result_flag:
                status_mapping = {'green':0,'yellow':1,'red':2}
                print status_mapping[stats_data['status']]
            else:
                print stats_data
        elif metrics_name == "node_status":
            if result_flag:
                print 1
            else:
                print 0
        else:
            if result_flag:
                print stats_data[metrics_name]
            else:
                print stats_data


if __name__ == "__main__":
    ExecFunByZabbixRequest(sys.argv[1:])