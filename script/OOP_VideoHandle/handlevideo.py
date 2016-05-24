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
import optparse
import baseclass
import subprocess
import xml.etree.ElementTree as ET

###############################################
#获取命令行参数
cmdopt = optparse.OptionParser(description="video handle related parameter",
                               prog="handlevideo.py" ,
                               version="1.0",
                               usage="%prog --vmatadata  video metadata information file     \
                                            --hadinsdir    hadoop install direction          \
                                            --nnport  hadoop namenode ipaddress+port         \
                                            --tasknums  tasktracker node numbers             \
                                            --blocksize hadoop block size                    \
                                            --hadversion  hadoop version                     \
                                            --loglevel setup log level                       \
                                            ")

cmdopt.add_option('-m','--vmatadata', help="video metadata information file")
cmdopt.add_option('-d','--hadinsdir', help="hadoop install direction")
cmdopt.add_option('-n','--nnport',    help="hadoop namenode ipaddress+port")
cmdopt.add_option('-t','--tasknums',  help="tasktracker node numbers")
cmdopt.add_option('-b','--blocksize', help="hadoop block size")
cmdopt.add_option('-v','--hadversion',help="hadoop version")
cmdopt.add_option('-l','--loglevel',  help="setup log level")

options,arguments = cmdopt.parse_args()

VideoMetaFile = options.vmatadata.strip()          #  --vmatadata

if options.hadinsdir == None:                      #  --hadinsdir
    HadoopInsDir = "/opt/hadoop/hadoop"
else:
    HadoopInsDir = options.hadinsdir.strip()
        
HadoopNNAddr = options.nnport.strip()              #  --nnport

TaskTrackerNums = int(options.tasknums.strip())    #  --tasknums
BlockSize = int(options.blocksize.strip())         #  --blocksize

HadoopVersion = options.hadversion.strip()         #  --hadversion
LogLevel = options.loglevel.strip()                #  --loglevel

##############################################

logger = baseclass.getlog("handlevideo",loglevel=LogLevel)

logger.debug("handle video parameter info : \n \
              VideoMetaFile: %s             \n \
              HadoopInsDir : %s             \n \
              HadoopNNAddr : %s             \n \
              TaskTrackerNums : %s          \n \
              BlockSize : %s                \n \
              HadoopVersion : %s            \n \
              LogLevel : %s                 \n \
              "%(VideoMetaFile,HadoopInsDir,HadoopNNAddr,TaskTrackerNums,BlockSize,HadoopVersion,LogLevel))

###############################################
#分析视频元数据文件,取到视频相关信息.
if not os.path.isfile(VideoMetaFile):
    logger.error("Don't find video metadata file : %s"%VideoMetaFile)
    sys.exit()
    
xmltree = ET.parse(VideoMetaFile)
xmlroot = xmltree.getroot()

VideoFileNameAlias = xmlroot.find("name").text
VideoFilePath = xmlroot.find("path").text

VideoBitRate = int(xmlroot.find("bitrate").text)
VideoFrameWidth = int(xmlroot.find("width").text)
VideoFrameHeight = int(xmlroot.find("height").text)
VideoDuration = float(xmlroot.find("duration").text)
VideoSize = int(xmlroot.find("size").text)

VideoFormat = xmlroot.find("format").text
IsWaterMark = xmlroot.find("wmark").text

if IsWaterMark == "True":
    IsWaterMark = True
    WaterMarkPath = xmlroot.find("wmarkpath").text
    LeftPixels = xmlroot.find("lpixels").text
    UpPixels = xmlroot.find("upixels").text
else:
    IsWaterMark = False

logger.debug("video metadata info :   \n  \
              VideoFileNameAlias : %s \n  \
              VideoFilePath : %s      \n  \
              VideoBitRate : %s       \n  \
              VideoFrameWidth : %s    \n  \
              VideoFrameHeight : %s   \n  \
              VideoDuration : %s      \n  \
              VideoSize : %s          \n  \
              VideoFormat : %s        \n  \
              IsWaterMark : %s        \n  \
              "%(VideoFileNameAlias,VideoFilePath,VideoBitRate,VideoFrameWidth,VideoFrameHeight,VideoDuration,VideoSize,VideoFormat,IsWaterMark))

#################################################
#重新初始化日志对象
logger = baseclass.getlog(VideoFileNameAlias,loglevel=LogLevel)

#初始化执行命令对象
RunCmdObj = baseclass.runCmd(logger)
#################################################

myselfdir = os.path.split(os.path.realpath(__file__))[0]

HadoopBinDir = HadoopInsDir + "/bin/hadoop"
HadoopStreamJarPath = HadoopInsDir + "/contrib/streaming/hadoop-streaming-%s.jar"%(HadoopVersion)

#################################################
""" 初始化目录 """

RunCmdObj.run(["mkdir /tmp/%s && mkdir /tmp/%s/inputfiles && mkdir /tmp/%s/avfiles"%(VideoFileNameAlias,VideoFileNameAlias,VideoFileNameAlias)])

#################################################
""" 视频初步处理 """

#如果原始文件不加水印且其帧高度小于等于360,则认为其就是"360p"播放文件,直接上传至HDFS,程序退出.
if not IsWaterMark and int(VideoFrameHeight) <= 360 :
    cmd = "%s fs -put %s hdfs://%s/%s/360p.%s"%(HadoopBinDir,VideoFilePath,HadoopNNAddr,VideoFileNameAlias,VideoFormat)
    RunCmdObj.run([cmd])
        
#如果原始文件不加水印且其帧高度大于360但小于等于480,则认为其就是"480p"播放文件,直接上传至HDFS.
if not IsWaterMark and 360 < int(VideoFrameHeight) <= 480 :
    cmd = "mv %s /tmp/%s/480p.%s"%(VideoFilePath,VideoFileNameAlias,VideoFormat)
    RunCmdObj.run([cmd])
    VideoFilePath = "/tmp/%s/480p.%s"%(VideoFileNameAlias,VideoFormat)
    
#如果原始文件不加水印且其帧高度大于480但小于等于720,则认为其就是"720p"播放文件,直接上传至HDFS.
if not IsWaterMark and 480 < int(VideoFrameHeight) <= 720 :
    cmd = "mv %s /tmp/%s/720p.%s"%(VideoFilePath,VideoFileNameAlias,VideoFormat)
    RunCmdObj.run([cmd])
    VideoFilePath = "/tmp/%s/720p.%s"%(VideoFileNameAlias,VideoFormat)

#如果原始文件不加水印且其帧高度大于720,则认为其就是"720p"播放文件,直接上传至HDFS.
if not IsWaterMark and int(VideoFrameHeight) > 720 :
    cmd = "mv %s /tmp/%s/720p.%s"%(VideoFilePath,VideoFileNameAlias,VideoFormat)
    RunCmdObj.run([cmd])
    VideoFilePath = "/tmp/%s/720p.%s"%(VideoFileNameAlias,VideoFormat)

###############################################
""" 收集元数据建立文件 """

if IsWaterMark:
    info_dict = {'name':VideoFileNameAlias,'format':VideoFormat,'width':VideoFrameWidth,'height':VideoFrameHeight,'bitrate':VideoBitRate,'leftpixels':LeftPixels,'uppixels':UpPixels}
else:
    info_dict = {'name':VideoFileNameAlias,'format':VideoFormat,'width':VideoFrameWidth,'height':VideoFrameHeight,'bitrate':VideoBitRate}
    
#建立hadoop集群信息
hadoopinfo_dict = {"HadoopNNAddr":HadoopNNAddr,"HadoopBinDir":HadoopBinDir}

###############################################
""" 分割视频 """
PerSecondSizeByte = operator.div(VideoSize,VideoDuration)
BlockSizeSecondNum = int(operator.div(BlockSize*1024*1024,PerSecondSizeByte))

PartNums = int(operator.itruediv(VideoDuration,BlockSizeSecondNum))+1

logger.debug("split video information : \n \
              PerSecondSizeByte : %s    \n \
              BlockSizeSecondNum : %s   \n \
              VideoSegNums : %s         \n \
             "%(PerSecondSizeByte,BlockSizeSecondNum,int(operator.itruediv(VideoDuration,BlockSizeSecondNum))+1))

###############################################
""" shell脚本分割视频 """
cmd = "cd /tmp/%s/ && /bin/sh %s/handleoffset.sh %s %s %s %s %s %s"
cmdstr = cmd%(VideoFileNameAlias,myselfdir,VideoFilePath,VideoFileNameAlias,VideoFormat,int(operator.itruediv(VideoDuration,BlockSizeSecondNum))+1,BlockSizeSecondNum,VideoDuration)
RunCmdObj.run([cmdstr])

###############################################
#分配每TaskTracker节点视频段数

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

i = PartNums
p = 0
for n in getPartsAssignList(PartNums,TaskTrackerNums):
    p = p+1
    while n > 0:
        #print "part%sv.mp4 , %s "%(i,p)
        cmdstr = "echo \"part%sv.%s\" >> /tmp/%s/inputfiles/video_%s"%(i,VideoFormat,VideoFileNameAlias,p)
        RunCmdObj.run([cmdstr])
        i=i-1
        n=n-1

#############################
#如需要加水印,将水印文件复制到带处理视频临时文件夹.
if IsWaterMark:
    cmd = "cp %s /tmp/%s/logo.png"%(WaterMarkPath,VideoFileNameAlias)
    RunCmdObj.run([cmd])
    
#############################
#上传文件到hdfs

cmd1 = "cd /tmp/%s && rm -f *.txt *.ts *part* ma.* mv.*"%(VideoFileNameAlias)
cmd2 = "%s fs -put /tmp/%s hdfs://%s/"%(HadoopBinDir,VideoFileNameAlias,HadoopNNAddr)
cmd3 = "rm -rf /tmp/%s/* "%(VideoFileNameAlias)
RunCmdObj.run([cmd1,cmd2,cmd3])

#############################

info_dict['segmentnums'] = int(operator.itruediv(VideoDuration,BlockSizeSecondNum))+1
info_dict['loglevel'] = LogLevel

RunCmdObj.run(["mkdir /tmp/%s/mrdata "%(VideoFileNameAlias)])

f = open('/tmp/%s/mrdata/video.info'%VideoFileNameAlias,'w')
pickle.dump(info_dict,f)
f.close()

f = open('/tmp/%s/mrdata/hadoop.info'%VideoFileNameAlias,'w')
pickle.dump(hadoopinfo_dict,f)
f.close()

cmd = "cp %s/mapper.py  %s/reducer.py  %s/baseclass.py /tmp/%s/mrdata/"%(myselfdir,myselfdir,myselfdir,VideoFileNameAlias)
RunCmdObj.run([cmd])

############################

logger.info("Web side handle %s.%s file complete"%(VideoFileNameAlias,VideoFormat))

logger.info("Start mapreducer handle,plase wait....")


cmd = "(time %s jar %s  -file /tmp/%s/mrdata/  -mapper mapper.py  -reducer reducer.py -input hdfs://%s/%s/inputfiles -output hdfs://%s/%s/%s -numReduceTasks 1) >> /tmp/videohandle.log 2>&1"
cmdstr = cmd%(HadoopBinDir,HadoopStreamJarPath,VideoFileNameAlias,HadoopNNAddr,VideoFileNameAlias,HadoopNNAddr,VideoFileNameAlias,VideoFileNameAlias)
RunCmdObj.run([cmdstr])














