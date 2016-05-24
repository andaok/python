#!/usr/bin/env python
# -*- encoding:utf-8

# -----------------------------------------------
# Purpose:
#     Backup data in accordance with the configuration 
# +   File
# Author : wye
# Date : 2016-05-16
# -------------------------------------------------

class BackupDir(object):

	def __init__(self,DirPath,ExceptSuffix,ExceptDir,ExceptFile):

		# ---------------------------------
		# Parameter description 
		# DirPath : directory path needed to be backup up
		# ExceptSuffix : if the file suffix is these will not be backed up
		# ExceptDir : directory path not needed to be backup up
		# ExceptFile : file path not be needed to be backup up
		# ---------------------------------

		self.DirPath = DirPath
		self.ExceptSuffix = ExceptSuffix
		self.ExceptDir = ExceptDir
		self.ExceptFile = ExceptFile

		
