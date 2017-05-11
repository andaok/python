from django.conf.urls import url
from jobapp import views

app_name = "jobapp"

urlpatterns = [
    url(r'^$',views.index,name="index"),
]