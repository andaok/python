#!/usr/bin/env python
# -*- encoding:utf-8 -*-

'''
Created on Oct 25, 2012

@author: wye

Copyright @ 2011 - 2012  Cloudiya Tech . Inc 
'''


"""
对视频进行分割
"""

import os
import sys
import time
import pickle
import random
import logging
import operator
import subprocess

###############################################
#分析视频元数据文件,取到视频相关信息.


###############################################
#分析视频元数据文件,取到视频相关信息.
#视频文件在web server存储路径
VideoFilePath = "/var/data/hadoop/video/IN/xhx72030.mp4"
#视频文件名

#ForDebug
str = ""
for i in range(8):
    str = chr(97 + random.randint(0,25)) + str

VideoFileNameAlias = str

#视频码率
VideoBitRate = "1500"
#视频分辨率
VideoFrameWidth = "1280"
VideoFrameHeight = "720"
#视频时长
VideoDuration = 1800.01
#视频大小
VideoSize = 366207700
#视频临时后缀格式
VideoFormat = "mp4"

#判断视频是否需要加水印，如需要，水印文件地址,距左边界像素,距上边界像素。
IsWaterMark = True
WaterMarkPath = "/tmp/logo60.png"
LeftPixels = "80"
UpPixels = "130"

###############################################
def getlog(VideoFileNameAlias,logfile="/tmp/videohandle.log"):
    logger = logging.Logger(VideoFileNameAlias)
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter("%(asctime)s -- [ %(name)s ] -- %(levelname)s -- %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger

def runSubprocess(cmd,STDIN=subprocess.PIPE,STDOUT=subprocess.PIPE,STDERR=subprocess.PIPE,timeout=1,logger=None):
    p = subprocess.Popen(cmd,shell=True,stdin=STDIN,stdout=STDOUT,stderr=STDERR)    
    p.wait()
    logger.error("Excute command stdout : %s"%(p.stdout.read()))
    if p.returncode != 0:
        logger.error("Excute command : %s fail,Error info : %s,Exit code : %s"%(cmd,p.stderr.read(),p.returncode))  
        return False
    return True  

def getPartsAssignList(PartNums,TaskTrackerNums):
    list = []
    for i in range(TaskTrackerNums):
        list.append(0)
        
    def listsum(list):
        sum = 0
        for i in list:
            sum = i + sum
        return sum
    
    loop = False
    while not loop:
        for i in range(TaskTrackerNums):
            list[i] = list[i]+1
            if listsum(list) == PartNums:
                loop = True
                break
    return list
###############################################

"""
初始化
"""
logger = getlog(VideoFileNameAlias)

myselfdir = os.path.split(os.path.realpath(__file__))[0]

HadoopInsDir = "/usr/local/src/lanhadoop/hadoopv101"

HadoopBinDir = HadoopInsDir + "/bin/hadoop"

HadoopStreamJarPath = HadoopInsDir + "/contrib/streaming/hadoop-streaming-1.0.1.jar"

HadoopNNAddr = "192.168.0.112:50081"

HadoopUser = "cloudiya"

MapReduceFileDir = "/var/data/python/Video/OOP"  

###########################
      
#创建目录
logger.info("Init temporary directory structure")

if not runSubprocess("mkdir /tmp/%s && mkdir /tmp/%s/inputfiles && mkdir /tmp/%s/avfiles"%(VideoFileNameAlias,VideoFileNameAlias,VideoFileNameAlias),logger=logger):
    sys.exit(101)

logger.info("Init temporary directory structure sucess!")

########################

#如果原始文件不加水印且其帧高度小于等于360,则认为其就是"360p"播放文件,直接上传至HDFS,程序退出.
if not IsWaterMark and int(VideoFrameHeight) <= 360 :
    #cmd = "sudo -u %s %s fs -put %s hdfs://%s/%s/360p.%s"%(HadoopUser,HadoopBinDir,VideoFilePath,HadoopNNAddr,VideoFileNameAlias,VideoFormat)
    cmd = "%s fs -put %s hdfs://%s/%s/360p.%s"%(HadoopBinDir,VideoFilePath,HadoopNNAddr,VideoFileNameAlias,VideoFormat)
    
    if not runSubprocess(cmd,logger=logger):
        sys.exit(110)
    logger.info("Generate 360p.%s files"%VideoFormat)
    sys.exit(100)
    
#如果原始文件不加水印且其帧高度大于360但小于等于480,则认为其就是"480p"播放文件,直接上传至HDFS.
if not IsWaterMark and 360 < int(VideoFrameHeight) <= 480 :
    cmd = "mv %s /tmp/%s/480p.%s"%(VideoFilePath,VideoFileNameAlias,VideoFormat)
    if not runSubprocess(cmd,logger=logger):
        sys.exit(110)
    logger.info("Generate 480p.%s files"%VideoFormat)
    VideoFilePath = "/tmp/%s/480p.%s"%(VideoFileNameAlias,VideoFormat)

    
#如果原始文件不加水印且其帧高度大于480但小于等于720,则认为其就是"720p"播放文件,直接上传至HDFS.
if not IsWaterMark and 480 < int(VideoFrameHeight) <= 720 :
    cmd = "mv %s /tmp/%s/720p.%s"%(VideoFilePath,VideoFileNameAlias,VideoFormat)
    if not runSubprocess(cmd,logger=logger):
        sys.exit(110)
    logger.info("Generate 720p.%s files"%VideoFormat)
    VideoFilePath = "/tmp/%s/720p.%s"%(VideoFileNameAlias,VideoFormat)

    
#如果原始文件不加水印且其帧高度大于720,则认为其就是"720p"播放文件,直接上传至HDFS.
if not IsWaterMark and int(VideoFrameHeight) > 720 :
    cmd = "mv %s /tmp/%s/720p.%s"%(VideoFilePath,VideoFileNameAlias,VideoFormat)
    if not runSubprocess(cmd,logger=logger):
        sys.exit(110)
    logger.info("Generate 720p.%s files"%VideoFormat)
    VideoFilePath = "/tmp/%s/720p.%s"%(VideoFileNameAlias,VideoFormat)
    
############################

#收集元数据建立文件
if IsWaterMark:
    info_dict = {'name':VideoFileNameAlias,'format':VideoFormat,'width':VideoFrameWidth,'height':VideoFrameHeight,'bitrate':VideoBitRate,'leftpixels':LeftPixels,'uppixels':UpPixels}
else:
    info_dict = {'name':VideoFileNameAlias,'format':VideoFormat,'width':VideoFrameWidth,'height':VideoFrameHeight,'bitrate':VideoBitRate}
    
#建立hadoop集群信息
hadoopinfo_dict = {"HadoopNNAddr":HadoopNNAddr,"HadoopBinDir":HadoopBinDir}

###############################################
    
"""
分割视频
"""
TaskTrackerNums = 3
BlockSize = 64
VideoSizeThreshold = ""

PerSecondSizeByte = operator.div(VideoSize,VideoDuration)
BlockSizeSecondNum = int(operator.div(BlockSize*1024*1024,PerSecondSizeByte))

PartNums = int(operator.itruediv(VideoDuration,BlockSizeSecondNum))+1

print VideoFileNameAlias
print PerSecondSizeByte
print BlockSizeSecondNum
print int(operator.itruediv(VideoDuration,BlockSizeSecondNum))+1

############################

cmd = "cd /tmp/%s/ && /bin/sh %s/handleoffset.sh %s %s %s %s %s %s"
cmdstr = cmd%(VideoFileNameAlias,myselfdir,VideoFilePath,VideoFileNameAlias,VideoFormat,int(operator.itruediv(VideoDuration,BlockSizeSecondNum))+1,BlockSizeSecondNum,VideoDuration)
logger.info("Excute command : %s "%cmdstr)
p = subprocess.Popen(cmdstr,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
p.wait()
if p.returncode != 0:
    logger.error("Excute command %s fail,Error info : %s,Exit code : %s"%(cmd,p.stdout.read(),p.returncode))
    sys.exit(105)

logger.info("%s"%(p.stdout.read()))

#############################

#分配每TaskTracker节点视频段数
logger.info("Start Calculate video part numbers per tasktracker node ")

i = PartNums
p = 0
for n in getPartsAssignList(PartNums,TaskTrackerNums):
    p = p+1
    while n > 0:
        #print "part%sv.mp4 , %s "%(i,p)
        cmdstr = "echo \"part%sv.%s\" >> /tmp/%s/inputfiles/video_%s"%(i,VideoFormat,VideoFileNameAlias,p)
        if not runSubprocess(cmdstr,logger=logger):
            sys.exit(106)
        i=i-1
        n=n-1

#############################

#如需要加水印,将水印文件复制到带处理视频临时文件夹.
if IsWaterMark:
    logger.info("Copy watermark picture to /tmp/%s"%VideoFileNameAlias)
    cmd = "cp %s /tmp/%s/logo.png"%(WaterMarkPath,VideoFileNameAlias)
    if not runSubprocess(cmd,logger=logger):sys.exit(107)
    
#############################

#上传文件到hdfs
logger.info("Clear up /tmp/%s directory,Ready to upload data to the hadoop."%VideoFileNameAlias)
if not runSubprocess("cd /tmp/%s && rm -f *.txt *.ts *part* ma.* mv.*"%(VideoFileNameAlias),logger=logger):
    sys.exit(108)

logger.info("Upload data to hdfs")
cmd = "%s fs -put /tmp/%s hdfs://%s/"%(HadoopBinDir,VideoFileNameAlias,HadoopNNAddr)
if not runSubprocess(cmd,logger=logger):sys.exit(109)
logger.info("Upload data to hdfs success")

#清除临时数据
if not runSubprocess("rm -rf /tmp/%s/* "%(VideoFileNameAlias),logger=logger):
    sys.exit(101)

#############################

info_dict['segmentnums'] = int(operator.itruediv(VideoDuration,BlockSizeSecondNum))+1


if not runSubprocess("mkdir /tmp/%s/mrdata "%(VideoFileNameAlias),logger=logger):
    sys.exit(101)

f = open('/tmp/%s/mrdata/video.info'%VideoFileNameAlias,'w')
pickle.dump(info_dict,f)
f.close()

f = open('/tmp/%s/mrdata/hadoop.info'%VideoFileNameAlias,'w')
pickle.dump(hadoopinfo_dict,f)
f.close()

cmd = "cp %s/mapper.py  %s/reducer.py /tmp/%s/mrdata/"%(MapReduceFileDir,MapReduceFileDir,VideoFileNameAlias)
if not runSubprocess(cmd,logger=logger):sys.exit(109)

############################

logger.info("Web side handle %s.%s file complete"%(VideoFileNameAlias,VideoFormat))

logger.info("Start mapreducer handle,plase wait....")

cmd = "%s jar %s  -file /tmp/%s/mrdata/  -mapper mapper.py  -reducer reducer.py -input hdfs://%s/%s/inputfiles -output hdfs://%s/%s/%s -numReduceTasks 1"
cmdstr = cmd%(HadoopBinDir,HadoopStreamJarPath,VideoFileNameAlias,HadoopNNAddr,VideoFileNameAlias,HadoopNNAddr,VideoFileNameAlias,VideoFileNameAlias)
if not runSubprocess(cmdstr,logger=logger):sys.exit(109)














