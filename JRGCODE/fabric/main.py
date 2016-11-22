#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---------------------------------------------------
# @Date    : 2016-11-21 16:53:54
# @Author  : wye
# @Version : V1.0
# @Desrc   : with fabric automated operation and 
#          + maintenance application cluster
# ---------------------------------------------------

from fabric.api import *
from fabric.context_managers import *


# Default env parameter
# Tomcat
env.tomcat_env_root = "~"
env.tomcat_home = env.tomcat_env_root + "/tomcat"
env.tomcat_dir_update = env.tomcat_env_root + "/update"
env.tomcat_dir_dest = env.tomcat_env_root + "/backup"
# Nginx






def load_env_data():
	pass


def prepare_data(appname,env):
	execute(load_env_data)
    execute(upload_data_to_tomcat_host)
	execute(upload_data_to_nginx_host)



@parallel
@roles("tomcat")
def upload_data_to_tomcat_host():
	pass




@roles("nginx")
@parallel
def upload_data_to_nginx_host():
	pass


@roles("nginx")
@parallel
def apphost_in_ng_down(apphost,apport):
	pass

@roles("nginx")
@parallel
def apphost_in_ng_up(apphost,apport):
	pass


def action_in_tomcat_host(apphost):
	pass


@roles("tomcat")
def deploy():
    execute(apphost_in_ng_down,env.host)
    execute(action_in_tomcat_host,env.host)
    execute(apphost_in_ng_up,env.host)    

(1) load_env_data


@roles("tomcat")
def action(action):
	if action == "deploy":
		execute(upload_data_to_tomcat_host)
	    execute(upload_data_to_nginx_host)
        execute(apphost_in_ng_down,env.host)
        execute(action_in_tomcat_host,env.host)
        execute(apphost_in_ng_up,env.host)  
    elif action == "stop":
        execute(apphost_in_ng_down,env.host)







    
        






