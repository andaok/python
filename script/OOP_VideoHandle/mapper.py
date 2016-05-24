#!/usr/bin/env python
# -*- encoding:utf-8 -*-

'''
Created on Nov 20, 2012

@author: wye

Copyright @ 2011 - 2012  Cloudiya Tech . Inc 
'''

"""
OOP of mapper code for Video handle  
"""

import os
import sys
import time
import pickle
import logging
import operator
import baseclass
import subprocess

######################################

class mapCmdOutput():
    
    """  Video mapper handle command output  """
    
    def __init__(self,info_dict,hadoopinfo_dict,seg_list,logger):
         
        self.VideoFileNameAlias = info_dict['name']
        self.VideoFrameWidth = int(info_dict['width'])
        self.VideoFrameHeight = int(info_dict['height'])
        self.VideoBitRate = int(info_dict['bitrate'])
        if info_dict.has_key("leftpixels"):self.LeftPixels = int(info_dict['leftpixels'])
        if info_dict.has_key("uppixels"):self.UpPixels = int(info_dict['uppixels'])
        
        self.HadoopNNAddr = hadoopinfo_dict["HadoopNNAddr"]
        self.HadoopBinDir = hadoopinfo_dict["HadoopBinDir"]
        
        self.SegVideoNameList = seg_list
        
        self.logger = logger
        
        self.FFmpegCmdList = []
        
        self.HadoopCmdList = []
    
    def getNewFrameWidth(self,NewFrameHeight):
        newwidth = int(self.VideoFrameWidth*int(NewFrameHeight)/self.VideoFrameHeight)
        if operator.mod(newwidth, 2) == 0:
            return newwidth
        else:
            return newwidth+1
    
    def addWm(self,wmwidth,nameflag):
        addWmCmd = "ffmpeg -i /tmp/%s/avfiles/%s -acodec copy -vcodec h264 -b %sk -vf \"movie=/tmp/%s/%s, scale=%s:-1 [wm];[in][wm] overlay=%s:%s [out]\" /tmp/%s/avfiles/%s.%s"
        for segname in self.SegVideoNameList:
            cmdstr = addWmCmd%(self.VideoFileNameAlias,segname,self.VideoBitRate,self.VideoFileNameAlias,"logo.png",int(wmwidth),self.LeftPixels,self.UpPixels,self.VideoFileNameAlias,nameflag,segname)   
            self.FFmpegCmdList.append(cmdstr)
            
    def addWmTcode(self,newbitrate,newwidth,height,wmwidth,nameflag):
        addWmTcodeCmd = "ffmpeg -y -threads 0 -i /tmp/%s/avfiles/%s -vcodec h264 -b %sk -s %sx%s -acodec copy -vf \"movie=/tmp/%s/%s, scale=%s:-1 [wm];[in][wm] overlay=%s:%s [out]\" /tmp/%s/avfiles/%s.%s"
        newwidth = self.getNewFrameWidth(height)
        for segname in self.SegVideoNameList:
            cmdstr = addWmTcodeCmd%(self.VideoFileNameAlias,segname,newbitrate,newwidth,height,self.VideoFileNameAlias,"logo.png",wmwidth,self.LeftPixels,self.UpPixels,self.VideoFileNameAlias,nameflag,segname) 
            self.FFmpegCmdList.append(cmdstr)
        
    def tranCode(self,newbitrate,newwidth,height,nameflag):
        tranCodeCmd = "ffmpeg -y -threads 0 -i /tmp/%s/avfiles/%s -vcodec h264 -b %sk -s %sx%s -acodec copy /tmp/%s/avfiles/%s.%s"
        newwidth = self.getNewFrameWidth(height)
        for segname in self.SegVideoNameList:
            cmdstr = tranCodeCmd%(self.VideoFileNameAlias,segname,newbitrate,newwidth,height,self.VideoFileNameAlias,nameflag,segname)
            self.FFmpegCmdList.append(cmdstr)
        
    def uploadData(self):
        uploadDataCmd = "%s fs -put /tmp/%s/avfiles/*.part* hdfs://%s/%s/avfiles/"
        cmdstr = uploadDataCmd%(self.HadoopBinDir,self.VideoFileNameAlias,self.HadoopNNAddr,self.VideoFileNameAlias)
        self.HadoopCmdList.append(cmdstr)

    #Start Output Commands   
    def initMapperEnv(self):
        CmdList = ["mkdir /tmp/%s && mkdir /tmp/%s/avfiles"%(self.VideoFileNameAlias,self.VideoFileNameAlias)]
        return CmdList
    
    def downVideoSegs(self):
        CmdList = []
        for segname in self.SegVideoNameList:
            cmdstr = "%s fs -get hdfs://%s/%s/avfiles/%s /tmp/%s/avfiles/"%(self.HadoopBinDir,self.HadoopNNAddr,self.VideoFileNameAlias,segname,self.VideoFileNameAlias)
            CmdList.append(cmdstr)
        return CmdList
    
    def downWaterMarkPic(self):
        if self.LeftPixels:
            CmdList = ["%s fs -get hdfs://%s/%s/logo.png /tmp/%s/logo.png"%(self.HadoopBinDir,self.HadoopNNAddr,self.VideoFileNameAlias,self.VideoFileNameAlias)]
            return CmdList
        else:
            return []
    
    def addWMarkORTCodeCmd(self):
        #加水印转码
        if self.LeftPixels:
            if self.VideoFrameHeight <= 360:
                #只加水印,不转码,生成有水印360p段.
                self.addWm(50,"360p")
                
            if 360 < self.VideoFrameHeight <= 480:
                #只加水印,不转码,生成有水印480p段.
                self.addWm(66,"480p")
        
                #加水印且转码成360p,生成有水印360p段
                newwidth = self.getNewFrameWidth("360")
                self.addWmTcode(300,newwidth,360,50,"360p")
                                
            if 480 < self.VideoFrameHeight <= 720:
                #只加水印,不转码,生成有水印720p段.
                self.addWm(100,"720p")
                
                #加水印且转码成480p,生成有水印480p段
                newwidth = self.getNewFrameWidth("480")
                self.addWmTcode(450,newwidth,480,66,"480p")
                
                #加水印且转码成360p,生成有水印360p段
                newwidth = self.getNewFrameWidth("360")
                self.addWmTcode(300,newwidth,360,50,"360p")
                
            if self.VideoFrameHeight > 720:
                #只加水印,不转码,生成有水印720p段.
                self.addWm(100,"720p")
                
                #加水印且转码成480p,生成有水印480p段
                newwidth = self.getNewFrameWidth("480")
                self.addWmTcode(450,newwidth,480,66,"480p")

                #加水印且转码成360p,生成有水印360p段
                newwidth = self.getNewFrameWidth("360")
                self.addWmTcode(300,newwidth,360,50,"360p")
                
        #只转码       
        else:
            if 360 < self.VideoFrameHeight <= 480:
                #只转码,转码成360p,生成360p段
                newwidth = self.getNewFrameWidth("360")
                self.tranCode(300,newwidth,360,"360p")
                
            if 480 < self.VideoFrameHeight <= 720:
                #只转码,转码成480p,生成480p段
                newwidth = self.getNewFrameWidth("480")
                self.tranCode(450,newwidth,480,"480p")
                
                #只转码,转码成360p,生成360p段
                newwidth = self.getNewFrameWidth("360")
                self.tranCode(300,newwidth,360,"360p")
                            
            if self.VideoFrameHeight > 720:
                #只转码,转码成480p,生成480p段
                newwidth = self.getNewFrameWidth("480")
                self.tranCode(450,newwidth,480,"480p")
                
                #只转码,转码成360p,生成360p段
                newwidth = self.getNewFrameWidth("360")
                self.tranCode(300,newwidth,360,"360p")
                                
        return self.FFmpegCmdList
            
    def uploadDataCmd(self):

        """
        if self.LeftPixels:
            if self.VideoFrameHeight <= 360:                
                #上传360p段到HDFS
                self.uploadData("360p")
                
            if 360 < self.VideoFrameHeight <= 480:                
                #上传360p段和480p段到HDFS
                self.uploadData("360p")
                self.uploadData("480p")
                
            if 480 < self.VideoFrameHeight <= 720:
                #上传360p,480p,720p段到HDFS
                self.uploadData("360p")
                self.uploadData("480p")
                self.uploadData("720p")

            if self.VideoFrameHeight > 720:
                #上传360p,480p,720p段到HDFS
                self.uploadData("360p")
                self.uploadData("480p")
                self.uploadData("720p")     
        else:
            if 360 < self.VideoFrameHeight <= 480:                
                #上传360p段到HDFS
                self.uploadData("360p")
                
            if 480 < self.VideoFrameHeight <= 720:
                #上传360p段和480p段到HDFS
                self.uploadData("360p")
                self.uploadData("480p")
            
            if self.VideoFrameHeight > 720:
                #上传360p段和480p段到HDFS
                self.uploadData("360p")
                self.uploadData("480p")
        """
        self.uploadData()              
        return self.HadoopCmdList
                
#######################################               
        
if __name__ == "__main__":
    
    logger = baseclass.getlog("Mapper")
    
    try:
        
        logger.info("Start mapper.....")
        
        #视频元数据
        info_dict = pickle.load(open('video.info','r'))

        #hadoop信息
        hadoopinfo_dict = pickle.load(open('hadoop.info','r'))
        
        #视频分段块
        seg_list = [line.strip() for line in sys.stdin]
        
    except Exception,e:
        logger.error("Mapper init exception: %s"%e)
        sys.exit()
        
    #重新初始化日志记录器
    logger = baseclass.getlog(info_dict['name'],loglevel=info_dict['loglevel'])
    
    try:
        RunCmdObj = baseclass.runCmd(logger)
        
        VideoObj = mapCmdOutput(info_dict,hadoopinfo_dict,seg_list,logger)
        
        RunCmdObj.run(VideoObj.initMapperEnv(),QuitFlag=False)
        
        if len(VideoObj.downWaterMarkPic()) > 0:RunCmdObj.run(VideoObj.downWaterMarkPic(),QuitFlag=False)
    
        RunCmdObj.run(VideoObj.downVideoSegs())
    
        RunCmdObj.run(VideoObj.addWMarkORTCodeCmd())
        
        RunCmdObj.run(VideoObj.uploadDataCmd())    
        
    except Exception,e:
        logger.error("Mapper handle exception %s"%e) 
        sys.exit()       
    
    #清理临时文件夹
    
    RunCmdObj.run(["rm -rf /tmp/%s/"%(info_dict['name'])],QuitFlag=False)
    
    logger.info("Mapper handle video complete") 
    


    
    
                    
