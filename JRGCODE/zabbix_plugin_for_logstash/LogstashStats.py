#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# -----------------------------------
# @Date     :  2017-08-18 16:55:00
# @Author   :  itwye
# @Version  :  v1.0
# @Descr    :  zabbix monitor plugin for logstash
# ----------------------------------

"""
Zabbix monitor plugin for logstash
"""

# ---------------------

import os
import sys
import json
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError

# ---------------------

LOGSTASH_HOST = "127.0.0.1"
LOGSTASH_PORT = 9600

# ---------------------

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
    """Execute function base zabbix request"""
    def __init__(self,paras):
        self.LOGSTASH_HOST = LOGSTASH_HOST
        self.LOGSTASH_PORT = LOGSTASH_PORT
        try:
            fun_obj = getattr(self,paras[0])
        except AttributeError:
            print "Don't find function ", paras[0]
        else:
            fun_obj(paras[1:])
    
    def get_total_input_events(self,paras):
        url = "http://%s:%s/_node/stats/pipeline"%(self.LOGSTASH_HOST,self.LOGSTASH_PORT)
        result_flag,stats_data = CallApiGetData(url)
        if result_flag:
            print stats_data['pipeline']['events']['in']
        else:
            print stats_data

    def get_total_filtered_events(self,paras):
        url = "http://%s:%s/_node/stats/pipeline"%(self.LOGSTASH_HOST,self.LOGSTASH_PORT)
        result_flag,stats_data = CallApiGetData(url)
        if result_flag:
            print stats_data['pipeline']['events']['filtered']
        else:
            print stats_data

    def get_total_output_events(self,paras):
        url = "http://%s:%s/_node/stats/pipeline"%(self.LOGSTASH_HOST,self.LOGSTASH_PORT)
        result_flag, stats_data = CallApiGetData(url)
        if result_flag:
            print stats_data['pipeline']['events']['out']
        else:
            print stats_data

    def get_event_avg_handle_time(self,paras):
        url = "http://%s:%s/_node/stats/pipeline"%(self.LOGSTASH_HOST,self.LOGSTASH_PORT)
        result_flag, stats_data = CallApiGetData(url)
        if result_flag:
            out_events = stats_data['pipeline']['events']['out']
            duration_in_millis = stats_data['pipeline']['events']['duration_in_millis']
            print int(duration_in_millis/out_events)
        else:
            print stats_data

    def get_logstash_live_status(self,paras):
        url = "http://%s:%s/_node/stats/pipeline"%(self.LOGSTASH_HOST,self.LOGSTASH_PORT)
        result_flag, stats_data = CallApiGetData(url)
        if result_flag:
            print 1
        else:
            print 0


if __name__ == "__main__":
    ExecFunByZabbixRequest(sys.argv[1:])





