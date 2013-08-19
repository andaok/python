#!/usr/bin/env python

# -*- encoding:utf-8 -*-

'''
Created on Jul 27, 2012
@author: wye 
@Copyright@2012 cloudiya technology 
'''

'''
Purpose :
      Commit customer server hardware information to cloudiya cloud verifyserver,retrieve registration code.

Quit Code Description :
      100 : Get register code success from verify server
      101 : Don't fetch serial number for main disk
      102 : Don't fetch MAC address for the first NIC
      103 : Connecting to verify server failure for send hardware information
      104 : Connecting to verify server failure for get register code
      105 : The serial number has been registered
      106 : serial number is invaild
      107 : serialnum is null from client side
      108 : generate registration code fail in verify server
'''

import os
import sys
import json
import socket
import fcntl
import struct
import time
import httplib
import random
import ConfigParser
import subprocess
import xml.etree.ElementTree as ET
from M2Crypto import RSA

ABSPath = os.path.abspath(sys.argv[0])
CloudiyaInsDir = (os.path.dirname(ABSPath)).rstrip("libexec")

configfile = CloudiyaInsDir+"services/etc/nimbus/workspace-service/auth.conf"
######################################
#Get static parameter form config file
######################################
config = ConfigParser.ConfigParser()
config.read(configfile)
CustomerInfoFile = CloudiyaInsDir+config.get("auth", "CustomerInfoFile")
RegCodeFile = CloudiyaInsDir+config.get("auth", "RegCodeFile")
vhostname = config.get("auth", "vhostname")
vport = config.get("auth", "vport")

##########################
#Check register code 
##########################
try:
    h = open(RegCodeFile,"rb")
except:
    pass
else:
    #print "RegCodeFile is already exist"
    sys.exit(100)
    
###########################
#Get software serial number
###########################
xmltree=ET.parse(CustomerInfoFile)
xmlroot=xmltree.getroot()
serialnum = xmlroot.find('serialnum').text.strip()

#################################
#Fetch server hardware infomation
#################################
p=subprocess.Popen("sudo hdparm -I /dev/sda | grep 'Serial Number' | awk -F: '{print $2}'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
if p.stderr.read() == "":
    realmaindisksn = p.stdout.read().strip()
else:
    #print "Don't fetch serial number for main disk"
    sys.exit(101)

#################################
def _ifinfo(sock, addr, ifname):
    iface = struct.pack('256s', ifname[:15])
    info = fcntl.ioctl(sock.fileno(), addr, iface)
    if addr == 0x8927:
        hwaddr = []
        for char in info[18:24]:
            if len(hex(ord(char))[2:]) == 1:
                str = (hex(ord(char))[2:]*2).upper()
            else:
                str = (hex(ord(char))[2:]).upper()
            hwaddr.append(str)
        return ':'.join(hwaddr)
    else:
        return socket.inet_ntoa(info[20:24])

def ifconfig(ifname):
    ifreq = {'ifname': ifname}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ifreq['addr'] = _ifinfo(sock, 0x8915, ifname) # SIOCGIFADDR
        ifreq['brdaddr'] = _ifinfo(sock, 0x8919, ifname) # SIOCGIFBRDADDR
        ifreq['netmask'] = _ifinfo(sock, 0x891b, ifname) # SIOCGIFNETMASK
        ifreq['hwaddr'] = _ifinfo(sock, 0x8927, ifname) # SIOCSIFHWADDR
    except:
        pass
    sock.close()
    return ifreq

INTERFACES_TO_CHECK = [ "em0", "em1","br0","eth0" ]

for iface in INTERFACES_TO_CHECK:
    ifreq = ifconfig(iface)
    if ifreq.has_key("hwaddr"):
        realmainnicmac = ifreq["hwaddr"]    
        break
    else:
        realmainnicmac = ""

if realmainnicmac == "":
    #print "Don't fetch MAC address for the first NIC"
    sys.exit(102)         
######################################
def getSerialNumUnit(num):
    serialnum = ""
    while len(serialnum) <  num:
        intnum = random.randint(0,25)
        lcletter = chr(97 + intnum)
        if serialnum.find(lcletter) == -1:
           serialnum  = serialnum + lcletter
    return serialnum.upper()

hardinfo ="WD-"+getSerialNumUnit(10)+"/"+realmaindisksn+"/"+getSerialNumUnit(10)+"/"+realmainnicmac+"/"+getSerialNumUnit(10)

####################################################################
#Encrypt hardware infomation with the secure transmission public key
####################################################################
stprikeystr =  xmlroot.find('stprikey').text
privatekey = RSA.load_key_string(stprikeystr)
encrypthardinfo = privatekey.private_encrypt(hardinfo,RSA.pkcs1_padding)


connection = httplib.HTTPConnection(vhostname+":"+vport)
header = {'Content-Type': 'application/x-www-form-urlencoded'}
connection.request('POST','/software/verify/st/'+serialnum,encrypthardinfo,header)
respmsg = connection.getresponse()
if respmsg.status == 200:
    result = respmsg.read()
    resultdict = json.loads(result)
else:
    #print "Connecting to verify server failure for send hardware information"
    sys.exit(103)    
#####################################################################
    
if resultdict["success"] == True:
    connection = httplib.HTTPConnection(vhostname+":"+vport)
    connection.request('GET','/software/verify/st/'+serialnum)
    respmsg = connection.getresponse()
    if respmsg.status == 200:
        result = respmsg.read()
        f = open(RegCodeFile,'w')
        f.write(result)
        f.close()
        #print str(resultdict["error"])
    else:
        #print "Connecting to verify server failure for get register code"
        sys.exit(104)
else:
    returnmsg = str(resultdict["error"])
    #print returnmsg
    if returnmsg.find("has been registered") > 0:
        sys.exit(105)
    if returnmsg.find("is invaild") > 0:
        sys.exit(106)
    if returnmsg.find("from client side") > 0:
        sys.exit(107)
    if returnmsg.find("registration code fail") > 0:
        sys.exit(108)         

sys.exit(100)
#####################################################################





