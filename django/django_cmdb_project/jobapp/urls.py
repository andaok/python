from django.conf.urls import url
from jobapp import views

app_name = "jobapp"

urlpatterns = [
    url(r'^$',views.index,name="index"),
    url(r'^get_app_info/$',views.get_appinfo_from_bking,name="get_app_info"),
    url(r'^get_set_info/$',views.get_setinfo_from_bking,name="get_set_info"),
    url(r'^get_module_info/$',views.get_moduleinfo_from_bking,name="get_module_info"),
    url(r'^target_hosts_info/$',views.target_hosts_info,name="target_hosts_info"),
]