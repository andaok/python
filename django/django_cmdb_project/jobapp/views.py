# -*- encoding:utf-8 -*-
#--------------------------------
# @Date    : 2017-05-10 15:00
# @Author  : wye
# @Version : v1.0
# @Desrc   : job control app views
# -------------------------------- 

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required


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



def get_job_host_task_status(host,jid):
    sql = "select full_ret from salt_returns where jid='%s' and id='%s'"%(jid,host)
    Records_num, Records_tuple = execute_sql(sql)
    if Records_num == 0 or Records_num == None:
        status = None
    else:
        status = json.loads(Records_tuple[0][0])['retcode']

    return status



@login_required
def index(request):    
    resp_info = {}
    resp_info['recent_all_jobs_nums'] = get_recent_all_jobs_nums()
    resp_info['recent_success_tasks_nums'] = get_recent_success_tasks_nums()
    resp_info['recent_failure_tasks_nums'] = get_recent_failure_tasks_nums()
    resp_info['recent_failure_tasks_info'] = get_recent_failure_tasks_info(10)
    resp_info['recent_succss_tasks_info'] = get_recent_succss_tasks_info(10)
    resp_info['running_jobs_nums'],resp_info['running_jobs_info'] = get_running_jobs_info()

    return render(request,'jobapp/index.html',resp_info)


@login_required
def get_appinfo_from_bking(request):
    appinfo = get_app_info()
    return JsonResponse(appinfo,safe=False)


@login_required
def get_setinfo_from_bking(request):
    app_field_name = request.GET['filter[filters][0][field]']
    app_id = request.GET['filter[filters][0][value]']
    setinfo = get_set_info(app_id)
    return JsonResponse(setinfo,safe=False)



@login_required
def get_moduleinfo_from_bking(request):
    set_name = request.GET['filter[filters][0][field]']
    set_id = request.GET['filter[filters][0][value]']
    moduleinfo = get_module_info(set_id)
    return JsonResponse(moduleinfo,safe=False)


@login_required
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




@login_required
def get_host_detail_info(request):
    hostname = request.GET['hostname']
    host_meta_info = get_host_meta_info(hostname)
    host_meta_info['osname_salt'] = host_meta_info['os'] + " " + host_meta_info['osrelease']
    host_meta_info['ip_salt'] = '|'.join(host_meta_info['ipv4'])

    return render(request,'jobapp/host_detail.html',{"host_detail_info":host_meta_info})





def auth_login(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('jobapp:index'))
            else:
                context['error_info'] = "%s ACCOUNT IS DISABLED!"%username
        else:
            context['error_info'] = "INVALID ACCOUNT!"
    

    return render(request,'jobapp/login.html',context)



@login_required
def auth_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('jobapp:login'))




@login_required
def get_failure_task_detail_info(request):
    context = {}
    jid = request.GET['jid']
    hostname = request.GET['hostname']
    sql = 'select full_ret from salt_returns where jid="%s" and id="%s"'%(jid,hostname)
    failure_task_num,failure_task_record_tuple =  execute_sql(sql)
    if failure_task_num != 0:
        failure_task_record = json.loads(failure_task_record_tuple[0][0])
        context['failure_task_record'] = failure_task_record  

    return render(request,'jobapp/failure_task_detail.html',context)




@login_required
def state_sls_job_execute(request):
    target_hosts = request.POST['show_target_hosts']
    action = request.POST['state_sls_select']
    is_test = request.POST.get('state_sls_is_test')
    
    target_hosts_list = target_hosts.split(",")
    target_hosts_num = len(target_hosts_list)

    if is_test == None:
        # Real execute job
        jid =  state_sls_job_execute_real(target_hosts_list,action)
    else:
        # test execute job
        jid =  state_sls_job_execute_real(target_hosts_list,action)

    return render(request,'jobapp/exec_result_show.html',{"target_hosts_list":target_hosts_list,"target_hosts_num":target_hosts_num,"jid":jid,"is_test":is_test})




@login_required
def get_job_hosts_task_status(request):
    hosts = request.GET['hosts']
    jid = request.GET['jid']
    
    host_list = hosts.split(",")
    hosts_status = []

    print "host_list is %s"%host_list

    for host in host_list:
        
        status = get_job_host_task_status(host,jid)

        print "info is %s %s %s"%(host , jid ,status)

        if status != None:
            host_status = {'host':host,'status':status}
            hosts_status.append(host_status)
    
    print "hosts_status is %s"%hosts_status

    #hosts_status = [{'host':'w26','status':1},{'host':'456','status':0}]

    return JsonResponse(hosts_status,safe=False)
    

# ----------------------
# FOR DEBUG
# ----------------------

if __name__ == "__main__":
    #print get_recent_failure_tasks_info(10)
    # print get_recent_succss_tasks_info(10)
    # print get_recent_all_jobs_nums()
    # print get_recent_failure_tasks_nums()
    # print get_recent_success_tasks_nums()
    #get_failure_task_detail_info_test("20170518140245899698","W612-JENKDOCK-3")
    #print get_job_host_task_status("W612-JENKDOCK-4","20170523140452702260")


    pass



