# -*- encoding:utf-8 -*-

'''
Created on Aug 28, 2012

@author: wye

Copyright @ 2012 cloudiya tech 
'''

import os
import sys
import random
import MySQLdb
import subprocess
import GlobalArgs
from M2Crypto import RSA

##########################
#Obtain the necessary parameters to generate the CPU authority
##########################
try:
    CloudSerialNum = sys.argv[1]
    IsCheck = sys.argv[2]
    MainNicMac = sys.argv[3]
    MainDiskID = sys.argv[4]
    CPUAuthNum = sys.argv[5]
except IndexError:
    raise Exception("Please re-set parameters,it need five parameters.")

def getSerialNumUnit(num):
    serialnum = ""
    while len(serialnum) <  num:
        intnum = random.randint(0,25)
        lcletter = chr(97 + intnum)
        if serialnum.find(lcletter) == -1:
           serialnum  = serialnum + lcletter
    return serialnum.upper()

CPUAuthSerialNum = getSerialNumUnit(8)

##########################
#Obtain publickey to decrypt CpuAuthRecrodfile 
##########################
try:
    w = open(GlobalArgs.keyspath+os.sep+CloudSerialNum+os.sep+"CAR"+"-"+'privatekey.pem','rb')
except IOError:
    raise Exception("Can not find the %s CAR-privatekey.pem"%(CloudSerialNum))
else:
    CPUAuthRePriKey = w.read()
    w.close()

###########################
#Create CPUAuthString
###########################
CPUAuthString = CPUAuthSerialNum+'_'+IsCheck+'_'+MainNicMac+'_'+MainDiskID+'_'+CPUAuthNum

###########################
#Encrypt CPUAuthString and write to CPUAuthfile
###########################
#privatekey = RSA.load_key(GlobalArgs.keyspath+os.sep+CloudSerialNum+os.sep+"CA"+"-"+'privatekey.pem')
#encryptCPUAuthString = privatekey.private_encrypt(CPUAuthString,RSA.pkcs1_padding)

publickey = RSA.load_pub_key(GlobalArgs.keyspath+os.sep+CloudSerialNum+os.sep+"CA"+"-"+'publickey.pem')
encryptCPUAuthString = publickey.public_encrypt(CPUAuthString,RSA.pkcs1_padding)

encryptCPUAuthBase64 = encryptCPUAuthString.encode("base64")

f = open(GlobalArgs.keyspath+os.sep+CloudSerialNum+os.sep+CPUAuthSerialNum+'.CA','w')
f.write(encryptCPUAuthBase64)
f.close()

'''
encryptCPUAuthString = encryptCPUAuthBase64.decode("base64")
publickey = RSA.load_pub_key(GlobalArgs.keyspath+os.sep+CloudSerialNum+os.sep+"CPUAUTH"+"-"+'publickey.pem')
decryptCPUAuthString = publickey.public_decrypt(encryptCPUAuthString,RSA.pkcs1_padding)

print decryptCPUAuthString
  
decryptCPUAuthList = decryptCPUAuthString.split('_')
print decryptCPUAuthList[5]
'''

###########################
#Write CPUAuth information to database
###########################
if subprocess.call("test -s %s"%(GlobalArgs.keyspath+os.sep+CloudSerialNum+os.sep+CPUAuthSerialNum+'.CA'),shell=True) == 0:
    dbconn = MySQLdb.connect(host=GlobalArgs.mysqlserver,user=GlobalArgs.mysqluser,passwd=GlobalArgs.mysqlpwd)
    dbcursor = dbconn.cursor()
    dbconn.select_db('SoftwareEncryption')
    value = [CloudSerialNum,CPUAuthSerialNum,CPUAuthNum,MainNicMac,MainDiskID,IsCheck]
    dbcursor.execute("insert into cpuauth (sn,CPUAuthSN,CPUAuthNum,MainNicMAC,MainDiskID,IsCheck,CreateTime) values(%s,%s,%s,%s,%s,%s,now())",value)
    dbcursor.close()
else:
    raise Exception("Create CPUAuth File failed for %s!"%(CloudSerialNum))
