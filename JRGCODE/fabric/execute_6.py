#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-11-22 17:12:14
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

from fabric.api import *
from fabric.context_managers import *
from fabric.contrib import *

env.roledefs = {
    "web":["weiye@172.29.22.27"],
    "db":["weiye@172.29.22.31"],
    "app":["weiye@172.29.22.27","weiye@172.29.22.31"]
}

env.passwords = {
    "weiye@172.29.22.27:22":"weiye",
    "weiye@172.29.22.31:22":"weiye"
}


env.warn_only = False

@roles("web")
def test1():
    run("/tmp/hello.sh")
    print "this is end"


@roles("web")
def test():
    put("/tmp/xiha.sh","/tmp/xiha.sh")
    print "this is end"