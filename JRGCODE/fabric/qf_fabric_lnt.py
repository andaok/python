#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---------------------------------------------------
# @Date    : 2016-11-21 16:53:54
# @Author  : wye
# @Version : V1.0
# @Desrc   : with fabric automated operation and 
#          + maintenance application cluster
# ---------------------------------------------------

import yaml
from fabric.api import *
from fabric.context_managers import *
from fabric.contrib import *


def load_env_data(AppName,AppEnv):
    try:
        yaml_file_path =  "env_quark_" + AppEnv + ".yaml"
        config_dict = yaml.load(file(yaml_file_path))[AppName]
        env.roledefs = config_dict["roledefs"]
        env.passwords = config_dict["passwords"]
        env.hostsconfs = config_dict["hostsconfs"]
        env.appconfs = config_dict["appconfs"]
        print env.roledefs
        print env.passwords
        print env.hostsconfs
        print env.appconfs 
    except yaml.YAMLError, e:
        abort("[Exception Quit,Error is]:\n %s"%e)


def prepare_data(**kwargs):
    AppName = kwargs["AppName"]
    AppEnv = kwargs["AppEnv"]
    execute(load_env_data,AppName,AppEnv)
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

# ---------------------------------------

@roles("nginx")
@parallel
def apphost_in_ng_down(apphost,apport):
    pass


def deploy(apphost):
    pass

@roles("nginx")
@parallel
def apphost_in_ng_up(apphost,apport):
    pass

# --------------------------------------

@roles("tomcat")
def work():
    execute(apphost_in_ng_down,env.host)
    execute(deploy,env.host)
    execute(apphost_in_ng_up,env.host)


# fab -f qf_fabric_lnt  prepare_data:AppName="mg-bkend",AppEnv="prod" work    