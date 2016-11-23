#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-11-22 15:57:43
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
from fabric.api import *

env.roledefs = {
    "web":["weiye@172.29.22.27"],
    "db":["weiye@172.29.22.31"]
}

env.passwords = {
    "weiye@172.29.22.27:22":"weiye",
    "weiye@172.29.22.31:22":"weiye"
}



def compare_file(LocalFilePath,RemoteFilePath):
    """
    Two files to compare if there is a change to upload 
    """
    pass


env.warn_only = True


@task    
@roles("web")    
def upload2():
    result = put("/tmp/script/xihahahah","/tmp/script1234")
    print result.failed

@task
@roles("web")
def upload1():
    result = run("/tmp/xiji.sh")
    print "failed is %s"%result.failed
    print "code is %s"%result.return_code