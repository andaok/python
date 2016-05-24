#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# ------------------------------ /
# GeTuiHttpInf interface
# @author: wye
# @date: 2014-11-18
# 个推HTTP接口
# ----------------------------- /

import ujson
from GeTuiHttpApi import GeTui
from bottle import Bottle,run,request

mybottle = Bottle()

@mybottle.route('/getuiapi',method='POST')
def getuiapi():
    MessageRawData = request.POST.get("message")
    GeTuiObj = GeTui(MessageRawData)
    GeTuiObj.start()                
application = mybottle