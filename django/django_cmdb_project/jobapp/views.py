from django.shortcuts import render
from django.http import HttpResponse

import json
import MySQLdb
from salt_api_sdk import *



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
    sql = "select count(*) from salt_returns where success=0"
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



# ----------------------
# FOR DEBUG
# ----------------------

if __name__ == "__main__":
    print get_recent_failure_tasks_info(10)
    # print get_recent_succss_tasks_info(10)
    # print get_recent_all_jobs_nums()
    # print get_recent_failure_tasks_nums()
    # print get_recent_success_tasks_nums()
   

