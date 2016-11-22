#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-11-18 21:37:07
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

from fabric.api import *

# Topic : connection attempts , timeout , skip_bad_hosts


env.connection_attempts = 3
env.timeout = 10
env.skip_bad_hosts = True

# The host of 172.29.22.28 is down  

env.roledefs = {
    "web":["weiye@172.29.22.28"],
    "db":["weiye@172.29.22.31"]
}

env.passwords = {
    "weiye@172.29.22.28:22":"weiye",
    "weiye@172.29.22.31:22":"weiye"
}


@roles("web","db")
def test():
	run("uptime")
	print "in %s end"%env.host


def go():
	execute(test)