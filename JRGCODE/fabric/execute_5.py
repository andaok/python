#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-11-22 15:57:43
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


@parallel
@roles("db","web")
def test1():
	print "test1"


@parallel
@roles("db","web")
def test2():
	print "test2"

@runs_once
def test():
	execute(test1)
	execute(test2)

@roles("db","web")
def go():
	execute(test)
	