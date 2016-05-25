#!/usr/bin/env python
# -*- encoding:utf-8 -*-

'''
Created on Feb 18, 2013

@author: wye

Copyright @ 2011 - 2012  Cloudiya Tech . Inc 
'''

import sys
import baseclass

FFPROBE="/usr/local/bin/ffprobe"

# Stream file path
StreamFilepath = sys.argv[1]

# Video file Name Alias
VideoAliasName = sys.argv[2] 

# Stream Property name
PropertyFlag = sys.argv[3]

logger = baseclass.getlog(VideoAliasName)
RunCmdObj = baseclass.runCmd(logger,VideoAliasName,False,False)

RunCmdObj.run(["%s -show_format %s"%(FFPROBE,StreamFilepath)])
VFormatList = baseclass.getVideoMetaDList(RunCmdObj.stdout,"FORMAT")

VFormatDict = VFormatList[0]

if PropertyFlag == "ab":print(VFormatDict["bit_rate"]) 


