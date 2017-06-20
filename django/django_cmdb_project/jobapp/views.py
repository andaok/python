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
from django.views.decorators.csrf import csrf_exempt

from jobapp.models import DynamicGroup , SaltGroup , action_audit

import os
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
    sql = 'select fun,jid,id,alter_time from salt_returns where success=1 and fun="%s" or fun="%s" or fun="%s" order by jid desc limit 0,%s'%("cmd.run","state.sls","cp.get_file",num)
    recent_success_tasks_nums,recent_success_tasks_records_tuple =  execute_sql(sql)
    # recent_success_tasks_records = {}
    # if recent_success_tasks_nums != 0:    
    #     for i in range(recent_success_tasks_nums):
    #         recent_success_tasks_records[i+1] = recent_success_tasks_records_tuple[i]

    # return recent_success_tasks_records
    return recent_success_tasks_records_tuple



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



def get_upload_job_host_task_status(host,jid):
    sql = "select full_ret from salt_returns where jid='%s' and id='%s'"%(jid,host)
    Records_num, Records_tuple = execute_sql(sql)
    if Records_num == 0 or Records_num == None:
        status = None
    else:
        status = json.loads(Records_tuple[0][0])['return']

    return status



def job_host_task_info(host,jid):
    sql = "select full_ret from salt_returns where jid='%s' and id='%s'"%(jid,host)
    _, Records_tuple = execute_sql(sql)
    return json.loads(Records_tuple[0][0])


def write_audit_info(jid,user):
    audit_info_obj = action_audit(jid=jid,user=user)
    audit_info_obj.save()



def get_jid_info(jid):
    sql = "select * from jids where jid='%s'"%jid
    Records_num, Records_tuple = execute_sql(sql)
    if Records_num != 0 and Records_num != None:
        return Records_tuple


@login_required
def index(request):    
    resp_info = {}
    #resp_info['recent_all_jobs_nums'] = get_recent_all_jobs_nums()
    #resp_info['recent_success_tasks_nums'] = get_recent_success_tasks_nums()
    #resp_info['recent_failure_tasks_nums'] = get_recent_failure_tasks_nums()
    resp_info['recent_failure_tasks_info'] = get_recent_failure_tasks_info(10)
    resp_info['recent_succss_tasks_info'] = get_recent_succss_tasks_info(10)
    #resp_info['running_jobs_nums'],resp_info['running_jobs_info'] = get_running_jobs_info()
    resp_info['last_days'] = get_keep_jobs_time()

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

    hostnames_list = []
    for host1 in hosts_list:
        hostnames_list.append(host1['HostName'])

    hosts_status = get_hosts_status(hostnames_list)


    for host in hosts_list:
        host['status'] = hosts_status.get(host['HostName'])
        if host['status']:
            host_meta_info = get_host_meta_info(host['HostName'])
            host['osname_salt'] = host_meta_info['os'] + " " + host_meta_info['osrelease']
            host['ip_salt'] = '|'.join(host_meta_info['ipv4'])
        else:
            pass

    target_hosts_info['hosts'] = hosts_list
    
    return render(request,'jobapp/target_hosts_info.html',target_hosts_info)


def hostname_base_bking_module(request):

    appid = request.GET['appid']
    setid = request.GET['setid']
    moduleid = request.GET['moduleid']
    hosts_list = get_hosts_info_by_module(appid,setid,moduleid)

    hostname_list = []

    for host in hosts_list:
        hostname_list.append(host['HostName'])

    #hostname_list = [{"hostname":"wer","hostid":"234"}]

    return JsonResponse(hostname_list,safe=False)



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
    user = request.user
    target_hosts = request.POST['show_target_hosts']
    action = request.POST['state_sls_select']
    is_test = request.POST.get('state_sls_is_test')
    
    target_hosts_list = target_hosts.split(",")
    target_hosts_num = len(target_hosts_list)

    jid = state_sls_execute(target_hosts_list,action,is_test)

    write_audit_info(jid,user)

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
 



@login_required
def get_upload_job_hosts_task_status(request):
    hosts = request.GET['hosts']
    jid = request.GET['jid']
    
    host_list = hosts.split(",")
    hosts_status = []

    for host in host_list:
        
        status = get_upload_job_host_task_status(host,jid)

        if status != None:
            if status != "" and status != "false":
                status = 0
            host_status = {'host':host,'status':status}
            hosts_status.append(host_status)
    
    return JsonResponse(hosts_status,safe=False)    



@login_required
def get_upload_file_progress(request):
    user = request.user
    user_dir = "/srv/salt/upload_files/%s/"%user

    hosts = request.GET['hosts']
    jid = request.GET['jid']
    source_file_name = request.GET["source_file_name"]
    dest_file_path = request.GET["dest_file_path"]
 
    source_file_path = os.path.join(user_dir,source_file_name)
    source_file_size = os.path.getsize(source_file_path)

    host_list = hosts.split(",")
    hosts_prog = []

    for host in host_list:
        try:
            size = get_file_stats(host,dest_file_path)[host]["size"]
        except KeyError:
            size = 0
        prog = "%.0f"%(float(size)/float(source_file_size)*100)
        host_prog = {'host':host,'prog':prog}
        hosts_prog.append(host_prog)

    return JsonResponse(hosts_prog,safe=False)



@login_required
def get_job_host_task_info(request):
    host = request.GET['host']
    jid = request.GET['jid']
    info = job_host_task_info(host,jid)
    return JsonResponse([{"info":info}],safe=False)



@login_required
def dynamic_group_manage(request):
    group_name = request.GET.get("group_name")
    group_members = request.GET.get("group_members")

    print "info is %s - %s"%(group_name,group_members)

    group_members_list = group_members.split(",")
    group_members_list = list(set(group_members_list))
    group_members = ",".join(group_members_list)
    
    retinfo = {}

    try:
        group_obj = DynamicGroup.objects.get(GroupName=group_name)
        group_obj.GroupMembers = group_members
        group_obj.save()
        retinfo["operate"] = "update group %s"%group_name
    except DynamicGroup.DoesNotExist:
        group_obj = DynamicGroup(GroupName=group_name,GroupMembers=group_members)
        group_obj.save()
        retinfo["operate"] = "create group %s"%group_name
   
    return JsonResponse(retinfo,safe=False)




@login_required
def dynamic_group_records(request):
    groups_obj = DynamicGroup.objects.order_by('id')
    groups_list = []
    for group_obj in groups_obj:
        group = {"id":group_obj.id,"GroupName":group_obj.GroupName,"GroupMembers":group_obj.GroupMembers}
        groups_list.append(group)
    return JsonResponse(groups_list,safe=False)




@login_required
def dynamic_group_record_by_id(request):
    id = request.GET.get("id")
    group_obj = DynamicGroup.objects.get(id=id)
    GroupMembers_Str = group_obj.GroupMembers
    GroupMembers_List = GroupMembers_Str.split(",")
    hostname_list = []
    for hostname in GroupMembers_List:
        hostname_list.append({"hostname":hostname,"hostid":"9999"})

    group = {"id":group_obj.id,"GroupName":group_obj.GroupName,"GroupMembers":hostname_list}
    return JsonResponse(group,safe=False)



@login_required
def dynamic_group_del_record_by_id(request):
    id = request.GET.get("id")
    DynamicGroup.objects.filter(id=id).delete()
    return JsonResponse({},safe=False)



@login_required
def dynamic_group_hosts_info(request):
    GroupName = request.GET.get("GroupName")
    GroupID = request.GET.get("GroupID")

    group_obj = DynamicGroup.objects.get(id=GroupID)
    GroupMembers_Str = group_obj.GroupMembers
    GroupMembers_List = GroupMembers_Str.split(",")

    hosts_list = []
    
    for hostname in GroupMembers_List:
        host = {}
        host["HostName"] = hostname
        host['status'] = get_host_status(host['HostName'])
        if host['status']:
            host_meta_info = get_host_meta_info(host['HostName'])
            host['osname_salt'] = host_meta_info['os'] + " " + host_meta_info['osrelease']
            host['ip_salt'] = '|'.join(host_meta_info['ipv4'])
        else:
            pass
        hosts_list.append(host)

    return render(request,'jobapp/dynamic_group_hosts_info.html',{"hosts":hosts_list,"GroupName":GroupName})




@login_required
def salt_group_manage(request):
    group_name = request.GET.get("group_name")
    group_expr = request.GET.get("group_expr")
    
    retinfo = {}

    try:
        group_obj = SaltGroup.objects.get(GroupName=group_name)
        group_obj.GroupExpr = group_expr
        group_obj.save()
        retinfo["operate"] = "update group %s"%group_name
    except SaltGroup.DoesNotExist:
        group_obj = SaltGroup(GroupName=group_name,GroupExpr=group_expr)
        group_obj.save()
        retinfo["operate"] = "create group %s"%group_name

    return JsonResponse(retinfo,safe=False)





@login_required
def salt_group_all(request):
    groups_obj = SaltGroup.objects.order_by('id')
    groups_list = []
    for group_obj in groups_obj:
        group = {"id":group_obj.id,"GroupName":group_obj.GroupName,"GroupExpr":group_obj.GroupExpr}
        groups_list.append(group)
    return JsonResponse(groups_list,safe=False)
 


@login_required
def salt_group_record_by_id(request):
    group_id = request.GET.get("group_id")
    group_obj = SaltGroup.objects.get(id=group_id)
    group = {"group_id":group_obj.id,"GroupName":group_obj.GroupName,"GroupExpr":group_obj.GroupExpr}
    return JsonResponse(group,safe=False)




@login_required
def salt_group_del_record_by_id(request):
    group_id = request.GET.get("group_id")
    SaltGroup.objects.filter(id=group_id).delete()
    return JsonResponse({},safe=False)




@login_required
def salt_group_hosts_info(request):
    group_id = request.GET.get('GroupID')
    group_name = request.GET.get('GroupName')
    
    group_obj = SaltGroup.objects.get(id=group_id)
    group_expr = group_obj.GroupExpr
    
    resp = get_salt_group_hosts(group_expr)

    hosts_list = []

    for hostname , host_obj in resp.iteritems():
        host = {}
        host["HostName"] = hostname
        host["status"] = 1
        host['osname_salt'] = host_obj['os'] + " " + host_obj['osrelease']
        host['ip_salt'] = '|'.join(host_obj['ipv4'])
        hosts_list.append(host)

    return render(request,"jobapp/salt_group_hosts_info.html",{"hosts":hosts_list,"GroupName":group_name})




@login_required
def cmd_run_job_execute(request):
    user = request.user
    target_hosts = request.POST['show_target_hosts']
    cmd = request.POST['cmd_run_str']
    cmd = cmd.replace("\r\n"," ")
    
    is_test = None

    target_hosts_list = target_hosts.split(",")
    target_hosts_num = len(target_hosts_list)

    if is_test == None:
        # Real execute job
        jid = cmd_run_job_execute_real(target_hosts_list,cmd)
    else:
        # test execute job
        jid = cmd_run_job_execute_test(target_hosts_list,cmd)

    write_audit_info(jid,user)

    return render(request,'jobapp/cmdrun_exec_result_show.html',{"target_hosts":target_hosts,"target_hosts_num":target_hosts_num,"jid":jid,"is_test":is_test})




@login_required
def upload_file_job_execute(request):
    user = request.user
    user_dir = "/srv/salt/upload_files/%s/"%user

    source_file_name = request.POST.get("source_file")
    target_hosts = request.POST.get("show_target_hosts")
    dest_dir = request.POST.get("dest_dir")

    target_hosts_list = target_hosts.split(",")
    target_hosts_num = len(target_hosts_list)
    source_file_path = os.path.join(user_dir,source_file_name)
    dest_file_path = dest_dir + os.sep + source_file_name
    
    source_file_size = os.path.getsize(source_file_path)/1024/1024

    jid = upload_file(target_hosts_list,user,source_file_name,dest_file_path)

    write_audit_info(jid,user)
    
    return render(request,'jobapp/upload_exec_result_show.html',{"target_hosts_list":target_hosts_list,"target_hosts_num":target_hosts_num,"jid":jid,"source_file_name":source_file_name,"dest_file_path":dest_file_path,"source_file_size":source_file_size})




@login_required
@csrf_exempt
def upload(request):
    user = request.user
    user_dir = "/srv/salt/upload_files/%s/"%user
    if not os.path.isdir(user_dir):os.makedirs(user_dir)
    if request.method == "POST":    
        myFile =request.FILES.get("files", None)    
        if not myFile:  
            return HttpResponse("no files for upload!")  
        destination = open(os.path.join(user_dir,myFile.name),'wb+')    
        for chunk in myFile.chunks():      
            destination.write(chunk)  
        destination.close()  
        return HttpResponse("")  




@login_required
def user_dir_files_list(request):
    user = request.user
    user_dir = "/srv/salt/upload_files/%s/"%user
    if not os.path.isdir(user_dir):
        os.makedirs(user_dir)
    filename_list = os.listdir(user_dir)
    files_list = []
    files_list.append({"FileName":"Please Select File..."})
    for filename in filename_list:
        file = {"FileName":filename}
        files_list.append(file)
    return JsonResponse(files_list,safe=False)



@login_required
def audit(request):
    actions_obj = action_audit.objects.order_by("-id")
    action_info_list = []
    for  action_obj in actions_obj:
        jid = action_obj.jid
        user = action_obj.user
        action_detail_info = json.loads(get_jid_info(jid)[0][1])
        tgt = action_detail_info['tgt']
        fun = action_detail_info['fun']
        arg = action_detail_info['arg']

        action_info = {"jid":jid,"user":user,"tgt":tgt,"fun":fun,"arg":arg}
        action_info_list.append(action_info)

    last_days = get_keep_jobs_time()
    return render(request,'jobapp/audit.html',{"action_info_list":action_info_list,"last_days":last_days})           



@login_required
def help(request):
    return render(request,'jobapp/help.html',{})


@login_required
def del_file(request):
    user = request.user
    user_dir = "/srv/salt/upload_files/%s/"%user
    file_name = request.GET.get("file_name")
    file_path = os.path.join(user_dir,file_name)
    os.remove(file_path)
    return JsonResponse({'info':'info'},safe=False)


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
    print json.loads(get_jid_info("20170608112713263763")[0][1])['arg']
    pass



