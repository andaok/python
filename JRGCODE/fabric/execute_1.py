#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-11-18 16:51:51
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$


### Fabric Topic : Failure handling

from fabric.api import *

env.roledefs = {
    "web":["weiye@172.29.22.27"],
    "db":["weiye@172.29.22.31"]
}

env.passwords = {
    "weiye@172.29.22.27:22":"weiye",
    "weiye@172.29.22.31:22":"weiye"
}


### (1) Part one 

#env.warn_only = True

@roles("db")
def error_test1():
    put("/tmp/nothisfile.sh","/tmp/nothisfile.sh")
    run("/bin/bash /tmp/nothisfileXIHA.sh")
    print "end"


### (2) Part two

@roles("web")
#@settings(warn_only=True)
def error_test2():
    put("/tmp/nothisfile.sh","/tmp/nothisfile.sh")
    run("/bin/bash /tmp/nothisfileXIHA.sh")
    print "end"


### (3) Part three

@roles("db")
def error_test3():
    with settings(warn_only=True):
        run("/bin/false")
        print "end"

### main 

def go():
    execute(error_test3)
