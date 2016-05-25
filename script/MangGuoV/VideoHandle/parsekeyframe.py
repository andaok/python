#!/usr/bin/env python
# -*- encoding:utf-8 -*-

'''
Created on 20131101

@author: wye

Copyright @ 2011 - 2012  Cloudiya Tech . Inc 
'''

'''
分析视频文件计算最优切割点
'''

import sys
import baseclass

videoname = sys.argv[1]
videomvpath = sys.argv[2]
VideoDuration = sys.argv[3]
BlockSizeSecondNum = int(sys.argv[4])
PartNums = int(sys.argv[5])

ffprobe="/usr/local/bin/ffprobe"
logger = baseclass.getlog(videoname)

KFTSobj = baseclass.getKFSplitPoint(logger,ffprobe,videoname,videomvpath,VideoDuration,BlockSizeSecondNum,PartNums)
print(KFTSobj.main())

