#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-11-18 14:50:55
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

from fabric.api import *

env.roledefs = {
    "web":["weiye@172.29.22.27"],
    "db":["weiye@172.29.22.31"]
}

env.passwords = {
    "weiye@172.29.22.27:22":"weiye",
    "weiye@172.29.22.31:22":"weiye"
}


@roles("db","web")
@parallel
def workhorse():
    print("env.host is %s , env.host_string is %s"%(env.host,env.host_string))
    return run("uname -r")


@roles("web")
def test():
    print("env.host is %s , env.host_string is %s"%(env.host,env.host_string))
    return run("uptime")

@task
def go():
    results1 = execute(workhorse)
    print results1
    results2 = execute(test)
    print results2



