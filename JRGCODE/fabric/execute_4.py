#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-11-21 15:21:27
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

from fabric.api import *
#from fabric.context_managers import *
#from fabric.contrib import *


env.roledefs = {
    "web":["weiye@172.29.22.27"],
    "db":["weiye@172.29.22.31"]
}

env.passwords = {
    "weiye@172.29.22.27:22":"weiye",
    "weiye@172.29.22.31:22":"weiye"
}


@roles("web","db")
def test():
	with settings(warn_only=True):
		with cd("/tmp"):
			run("/bin/bash xihahaha.sh")

def go():
	result = execute(test)
	print result
