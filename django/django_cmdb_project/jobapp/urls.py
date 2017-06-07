from django.conf.urls import url
from jobapp import views

app_name = "jobapp"

urlpatterns = [
    url(r'^$',views.index,name="index"),
    url(r'^get_app_info/$',views.get_appinfo_from_bking,name="get_app_info"),
    url(r'^get_set_info/$',views.get_setinfo_from_bking,name="get_set_info"),
    url(r'^get_module_info/$',views.get_moduleinfo_from_bking,name="get_module_info"),
    url(r'^target_hosts_info/$',views.target_hosts_info,name="target_hosts_info"),
    url(r'^get_host_detail_info/$',views.get_host_detail_info,name="get_host_detail_info"),
    url(r'^login/$',views.auth_login,name="login"),
    url(r'^logout/$',views.auth_logout,name="logout"),
    url(r'^get_failure_task_detail_info/$',views.get_failure_task_detail_info,name="get_failure_task_detail_info"),
    url(r'^state_sls_job_execute/$',views.state_sls_job_execute,name="state_sls_job_execute"),
    url(r'^get_job_hosts_task_status/$',views.get_job_hosts_task_status,name="get_job_hosts_task_status"),
    url(r'^get_job_host_task_info/$',views.get_job_host_task_info,name="get_job_host_task_info"),
    url(r'^hostname_base_bking_module/$',views.hostname_base_bking_module,name="hostname_base_bking_module"),
    url(r'^dynamicgroup/manage/$',views.dynamic_group_manage,name="dynamic_group_manage"),
    url(r'^dynamicgroup/show/$',views.dynamic_group_records,name="dynamic_group_show"),
    url(r'^dynamicgroup/get/id/$',views.dynamic_group_record_by_id,name="dynamic_group_record_by_id"),
    url(r'^dynamicgroup/del/id/$',views.dynamic_group_del_record_by_id,name="dynamic_group_del_record_by_id"),
    url(r'^dynamic_group_hosts_info/$',views.dynamic_group_hosts_info,name="dynamic_group_hosts_info"),
    url(r'^saltgroup/manage/$',views.salt_group_manage,name="salt_group_manage"),
    url(r'^saltgroup/all/$',views.salt_group_all,name="salt_group_all"),
    url(r'^saltgroup/get/id/$',views.salt_group_record_by_id,name="salt_group_record_by_id"),
    url(r'^saltgroup/del/id/$',views.salt_group_del_record_by_id,name="salt_group_del_record_by_id"),
    url(r'^salt_group_hosts_info/$',views.salt_group_hosts_info,name="salt_group_hosts_info"),
    url(r'^cmd_run_job_execute/$',views.cmd_run_job_execute,name="cmd_run_job_execute"),
    url(r'^upload_file_job_execute/$',views.upload_file_job_execute,name="upload_file_job_execute"),
    url(r'^upload/$',views.upload,name="upload"),
    url(r'^user/files/show/$',views.user_dir_files_list,name="user_files_show"),
]
