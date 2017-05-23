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
]
