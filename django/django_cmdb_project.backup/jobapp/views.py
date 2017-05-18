# -*- encoding:utf-8 -*-
#--------------------------------
# @Date    : 2017-05-10 15:00
# @Author  : wye
# @Version : v1.0
# @Desrc   : job control app views
# -------------------------------- 

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse


import json
import MySQLdb
from salt_api_sdk import *
from bk_cmdb_api import *



# -----------------------------------------
# MYSQL SERVER INFO
# -----------------------------------------
MysqlServer = "127.0.0.1"
MysqlUser = "root"
MysqlPasswd = ""
MysqlDB = "salt"
# -----------------------------------------


def execute_sql(sql):
    try:
        DBConn = MySQLdb.connect(host=MysqlServer,user=MysqlUser,passwd=MysqlPasswd)
        DBCursor = DBConn.cursor()
        DBConn.select_db(MysqlDB)
        RecordNums = DBCursor.execute(sql)
        if RecordNums == 0 or RecordNums == None:
            RecordNums = 0
            RecordSets = ()
        else:
           RecordSets = DBCursor.fetchall()
           DBConn.commit()
        return RecordNums , RecordSets
    except Exception,e:
        print (" Execute sql error,error is %s"%e)
    finally:
        DBConn.close()
        DBCursor.close()



def get_recent_failure_tasks_info(num=10):

    sql = 'select fun,jid,id,alter_time from salt_returns  \n \
           where fun <> "runner.jobs.active"  \n \
           and fun <> "saltutil.running"  \n \
           and success=0 order by jid desc limit 0,%s'%num

    recent_failure_tasks_nums,recent_failure_tasks_records_tuple =  execute_sql(sql)
    return recent_failure_tasks_records_tuple



def get_recent_failure_tasks_nums():

    sql = 'select count(*) from salt_returns  \n \
           where fun <> "runner.jobs.active"  \n \
           and fun <> "saltutil.running"  \n \
           and success=0'

    _ , Records_tuple = execute_sql(sql)
    recent_failure_tasks_nums = Records_tuple[0][0]
    return recent_failure_tasks_nums



def get_recent_succss_tasks_info(num=10):
    sql = 'select fun,jid,id from salt_returns where success=1 order by jid desc limit 0,%s'%num
    recent_success_tasks_nums,recent_success_tasks_records_tuple =  execute_sql(sql)
    recent_success_tasks_records = {}
    if recent_success_tasks_nums != 0:    
        for i in range(recent_success_tasks_nums):
            recent_success_tasks_records[i+1] = recent_success_tasks_records_tuple[i]

    return recent_success_tasks_records



def get_recent_success_tasks_nums():
    sql = "select count(*) from salt_returns where success=1"
    _ , Records_tuple = execute_sql(sql)
    recent_success_tasks_nums = Records_tuple[0][0]
    return recent_success_tasks_nums



def get_recent_all_jobs_nums():
    sql = "select count(*) from jids"
    _ , Records_tuple = execute_sql(sql)
    recent_all_jobs_nums = Records_tuple[0][0]
    return recent_all_jobs_nums
    


def index(request):    
    resp_info = {}
    resp_info['recent_all_jobs_nums'] = get_recent_all_jobs_nums()
    resp_info['recent_success_tasks_nums'] = get_recent_success_tasks_nums()
    resp_info['recent_failure_tasks_nums'] = get_recent_failure_tasks_nums()
    resp_info['recent_failure_tasks_info'] = get_recent_failure_tasks_info(10)
    resp_info['recent_succss_tasks_info'] = get_recent_succss_tasks_info(10)
    resp_info['running_jobs_nums'],resp_info['running_jobs_info'] = get_running_jobs_info()

    return render(request,'jobapp/index.html',resp_info)



def get_appinfo_from_bking(request):
    appinfo = get_app_info()
    return JsonResponse(appinfo,safe=False)



def get_setinfo_from_bking(request):
    app_field_name = request.GET['filter[filters][0][field]']
    app_id = request.GET['filter[filters][0][value]']
    setinfo = get_set_info(app_id)
    return JsonResponse(setinfo,safe=False)



def get_moduleinfo_from_bking(request):
    set_name = request.GET['filter[filters][0][field]']
    set_id = request.GET['filter[filters][0][value]']
    moduleinfo = get_module_info(set_id)
    return JsonResponse(moduleinfo,safe=False)



def target_hosts_info(request):
    target_hosts_info = {}
    appid = request.GET['app'].split("_")[0]
    appname = request.GET['app'].split("_")[1]

    setid = request.GET['set'].split("_")[0]
    setname = request.GET['set'].split("_")[1]

    moduleid = request.GET['module'].split("_")[0]
    modulename = request.GET['module'].split("_")[1]
    
    target_hosts_info["appname"] = appname
    target_hosts_info["setname"] = setname
    target_hosts_info["modulename"] = modulename

    hosts_list = get_hosts_info_by_module(appid,setid,moduleid)

    for host in hosts_list:
        host['status'] = get_host_status(host['HostName'])
        if host['status']:
            host_meta_info = get_host_meta_info(host['HostName'])
            host['osname_salt'] = host_meta_info['os'] + " " + host_meta_info['osrelease']
            host['ip_salt'] = '|'.join(host_meta_info['ipv4'])
        else:
            pass

    target_hosts_info['hosts'] = hosts_list
    
    return render(request,'jobapp/target_hosts_info.html',target_hosts_info)


def get_host_detail_info(request):
    hostname = request.GET['hostname']
    host_meta_info = get_host_meta_info(hostname)
    host_meta_info['osname_salt'] = host_meta_info['os'] + " " + host_meta_info['osrelease']
    host_meta_info['ip_salt'] = '|'.join(host_meta_info['ipv4'])

    return render(request,'jobapp/host_detail.html',{"host_detail_info":host_meta_info})

# ----------------------
# FOR DEBUG
# ----------------------

if __name__ == "__main__":
    #print get_recent_failure_tasks_info(10)
    # print get_recent_succss_tasks_info(10)
    # print get_recent_all_jobs_nums()
    # print get_recent_failure_tasks_nums()
    # print get_recent_success_tasks_nums()
    pass



