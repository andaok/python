#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# -----------------------------------
# @Date     :  2017-08-16 17:38:00
# @Author   :  wye
# @Version  :  v1.0
# @Descr    :  monitor for redis
# ----------------------------------

"""
This script is divided two stages,
The first stage to achieve monitor key metrics for redis in elk,
The second stage to achieve monitor all base metrics for redis. 
"""

import sys
import json

import redis

# --------------------

REDIS_HOST = "127.0.0.1"
REDIS_PORT = "6379"
REDIS_DB = 0

LOG_EVENT_LISTS = ['filebeat-java-1','filebeat-java-2','filebeat-java-2']

# --------------------

def get_redis_exec_obj():
    redis_pool = redis.ConnectionPool(host=REDIS_HOST,port=REDIS_PORT,db=REDIS_DB)
    redis_exec_obj = redis.Redis(connection_pool=redis_pool)
    return redis_exec_obj


class ExecFunByZabbixRequest(object):
    """Execute functions based on zabbix request """
    def __init__(self, paras):
        self.LOG_EVENT_LISTS = LOG_EVENT_LISTS
        try:
            fun_obj = getattr(self,paras[0])
        except AttributeError:
            print "without this function of %s"%(paras[0])
        else:
            fun_obj(paras[1:])

    def log_event_list_discovery(self,paras):
        """
        Return the list to be monitored to zabbix server
        """
        tmp_dict = {}
        tmp_list = []

        if self.LOG_EVENT_LISTS:
            for name in self.LOG_EVENT_LISTS:
                tmp_list.append({"{#LISTNAME}":name})
        tmp_dict['data'] = tmp_list
        print json.dumps(tmp_dict)     
    
    def get_pong(self,paras):
        """
        Check redis status
        """
        try:
            redis_exec_obj = get_redis_exec_obj()
            redis_exec_obj.ping()
        except redis.exceptions.ConnectionError,ex:
            print 0
        else:
            print 1

    def get_list_member_number(self,paras):
        """
        Get list member number
        """
        redis_exec_obj = get_redis_exec_obj()
        print redis_exec_obj.llen(paras[0])
    
    def get_redis_used_memory(self,paras):
        """
        Get redis consumes memory (byte)
        """
        redis_exec_obj = get_redis_exec_obj()
        print redis_exec_obj.info()['used_memory']


if __name__ == "__main__":
    
    ExecFunByZabbixRequest(sys.argv[1:])

