
from django.conf.urls import url
from xcmdb_main import views

app_name = "xcmdb_main"

urlpatterns = [
    url(r'^$',views.index,name="index"),
    url(r'^login/$',views.auth_login,name="auth_login"),
    url(r'^logout/$',views.auth_logout,name="auth_logout"),
    url(r'^sum/$',views.global_sum,name="global_sum"),
    url(r'^add_host/$',views.add_host,name="add_host"),
    url(r'^manage_host/$',views.manage_host,name="manage_host"),
    url(r'^query/$',views.query_service,name="query_service"),
    url(r'^exec_job/$',views.exec_job,name="exec_job"),
    url(r'^help/$',views.help_service,name="help_service"),
]
