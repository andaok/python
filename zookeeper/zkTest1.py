#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-08-24 10:51:21
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

# set file to zookeeper by zkset
# get file from zookeeper by zkget

import logging
import kazoo
from kazoo.client import KazooClient

logging.basicConfig()

def zkset():

    file = "/tmp/redis_config.properties"

    zk = KazooClient(hosts='172.29.22.15:2181')
    zk.start()

    f=open(file,'rb')
    m=f.read()

    #Ensure a path , Create if necessary.
    zk.ensure_path("/instances/dev_conf/webapps/qf-app-bkend/WEB-INF/classes")
    #Create a node with data.
    try:
        zk.create("/instances/dev_conf/webapps/qf-app-bkend/WEB-INF/classes/redis_config.properties",m)
    except kazoo.exceptions.NodeExistsError:
        zk.set("/instances/dev_conf/webapps/qf-app-bkend/WEB-INF/classes/redis_config.properties",m)


    zk.stop()


def zkget():

    file = "/tmp/redis_config.properties.get"

    zk = KazooClient(hosts='172.29.22.15:2181')
    zk.start()

    f=open(file,'wb')
    f.write(zk.get(path="/instances/dev_conf/webapps/qf-app-bkend/WEB-INF/classes/redis_config.properties")[0])
    f.close()

    zk.stop()


#zkset()
zkget()


