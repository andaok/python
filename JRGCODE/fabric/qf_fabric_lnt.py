#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---------------------------------------------------
# @Date    : 2016-11-21 16:53:54
# @Author  : wye
# @Version : V1.0
# @Desrc   : with fabric automated operation and 
#          + maintenance application cluster
# ---------------------------------------------------

import os
import yaml
from fabric.api import *
from fabric.context_managers import *
from fabric.contrib import *


# Fabric env parameter
env.warn_only = True


# Default env parameter
env.DefaultParas = {
    #Tomcat
    "tomcat_home_dir" : "~/tomcat",
    "tomcat_update_dir" : "~/update",
    "tomcat_backup_dir" : "~/backup",
    "tomcat_deploy_scripts_dir" : "~/deploy",
    #Nginx
    "nginx_deploy_scripts_dir" : "~/deploy"
}


# Local work parameter
env.base_dir = os.path.dirname(__file__)
env.yaml_dir = env.base_dir + "/env"
env.deploy_scripts_dir = env.base_dir + "/scripts"


def get_parameter_value(AppHost,ParaName):
    """
    If the parameter is set in the yaml file , use the parameter value in yaml file.
    If not , using the default value.
    """
    try:
        if env.hostsconfs.has_key("AppHost"):
            if env.hostsconfs["AppHost"].has_key("ParaName"):
                return env.hostsconfs["AppHost"]["ParaName"]
            else:
                return env.DefaultParas["ParaName"]
        else:
            return env.DefaultParas["ParaName"]
    except Exception ,e:
        abort("[get_parameter_value][Exception Quit,Error is]:\n %s"%e)
    
    
def load_env_data(AppName,AppEnv):
    """
    Load env data from yaml faile.
    """
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
        abort("[load_env_data][Exception Quit,Error is]:\n %s"%e)


def prepare_data(**kwargs):
    """
    Prepare data for the following tasks
    """
    AppName = kwargs["AppName"]
    AppEnv = kwargs["AppEnv"]
    execute(load_env_data,AppName,AppEnv)
    execute(upload_data_to_tomcat_host)
    execute(upload_data_to_nginx_host)



@parallel
@roles("tomcat")
def upload_data_to_tomcat_host():
    """
    Upload app package and deploy scripts to host
    """
    local_scripts_dir = env.deploy_scripts_dir
    remote_scripts_dir = get_parameter_value(env.host,"tomcat_deploy_scripts_dir")
    run("mkdir -p %s"%remote_scripts_dir)
    result1 = put("%s/*"%local_scripts_dir,remote_scripts_dir)
    if result1.failed:
       abort("[upload_data_to_tomcat_host][Exception Quit,Error is]:\n %s"%result1.failed)
    
    local_package_path = env.appconfs["deploy_package_path"]
    remote_package_dir = get_parameter_value(env.host,"tomcat_update_dir")
    run("mkdir -p %s"%remote_package_dir)
    result2 = put(local_package_path,remote_package_dir)
    if result2.failed:
       abort("[upload_data_to_tomcat_host][Exception Quit,Error is]:\n %s"%result2.failed)


@parallel
@roles("nginx")
def upload_data_to_nginx_host():
    """
    Upload deploy scripts to host
    """
    local_scripts_dir = env.deploy_scripts_dir
    remote_scripts_dir = get_parameter_value(env.host,"nginx_deploy_scripts_dir")
    run("mkdir -p %s"%remote_scripts_dir)
    result = put("%s/*"%local_scripts_dir,remote_scripts_dir)
    if result.failed:
       abort("[upload_data_to_nginx_host][Exception Quit,Error is]:\n %s"%result.failed)



# ---------------------------------------

@roles("nginx")
@parallel
def apphost_in_ng_down(apphost,apport):
    pass


def do_action(AppHost):
    """
    Call shell script to stop,deploy,start tomcat
    """

    action = "deploy"
    remote_script_path = get_parameter_value(env.host,"tomcat_deploy_scripts_dir") + "/%s.sh"%action
    tomcat_home_dir = get_parameter_value(AppHost,"tomcat_home_dir")
    deploy_package_name = env.appconfs["deploy_package_name"]
    tomcat_backup_dir = get_parameter_value(AppHost,"tomcat_backup_dir")
    tomcat_update_dir =  get_parameter_value(AppHost,"tomcat_update_dir")
    check_url = env.hostsconfs[AppHost]["check_url"]

    argscmd = "--ACTION %s --TOMCAT_HOME %s  --APP_NAME %s --dir_src  %s --dir_dest %s --dir_update %s --CHECK_URL %s" 
    args = argscmd%(action, tomcat_home_dir,deploy_package_name,"NOANYVALUE", tomcat_backup_dir, dir_update, check_url)

    result = run('set -m; %s %s' % (remote_script_path, args))
    if result.failed:
        abort("[do_action][deploy][Exception Quit Code is %s]"%(result.return_code))


@roles("nginx")
@parallel
def apphost_in_ng_up(apphost,apport):
    pass

# --------------------------------------

@roles("tomcat")
def work():
    execute(apphost_in_ng_down,env.host)
    execute(do_action,env.host)
    execute(apphost_in_ng_up,env.host)


# fab -f qf_fabric_lnt  prepare_data:AppName="mg-bkend",AppEnv="prod" work    