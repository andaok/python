#!/usr/bin/env python

'''
Created on 2012-7-30
@author: wye 
@Copyright@2012 cloudiya technology 
'''
'''
Purpose : 
    Verify that the customer is an authorized user

Quit Code Description :
      100 : Verify success
      101 : Don't fetch serial number for main disk
      102 : Don't fetch MAC address for the first NIC
      103 : Don't find register code file in localhost
      104 : Connecting to verify server failure for Get ED public key
      105 : Hardware information does not match,verify failure.
      106 : ED publickey file or register code file format error
 '''

import os
import sys
import random
import socket
import fcntl
import struct
import time
import subprocess
import httplib
import ConfigParser
import M2Crypto
from M2Crypto import RSA
import xml.etree.ElementTree as ET

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
EDPubKeyFile = CloudiyaInsDir+config.get("auth", "EDPubKeyFile")
vhostname = config.get("auth", "vhostname")
vport = config.get("auth", "vport")

###########################
#Get software serial number
###########################
xmltree=ET.parse(CustomerInfoFile)
xmlroot=xmltree.getroot()
serialnum = xmlroot.find('serialnum').text.strip()

###################################
#Fetch server hardware infomation
###################################
p=subprocess.Popen("sudo hdparm -I /dev/sda | grep 'Serial Number' | awk -F: '{print $2}'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
if p.stderr.read() == "":
    realmaindisksn = p.stdout.read().strip()
else:
    #print "Don't fetch serial number for main disk"
    sys.exit(101)

###################################
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
                       
###################################
#Verify that the customer is an authorized user
###################################
try:
    w = open(RegCodeFile,'rb')
except IOError:
    #print "Don't find register code file in localhost"
    sys.exit(103)
else:
    data = w.read()
    w.close()
    
#####################################
try:
    w = open(EDPubKeyFile,'rb')
except:
    connection = httplib.HTTPConnection(vhostname+":"+vport)
    connection.request('GET','/software/verify/ed/'+serialnum)
    respmsg = connection.getresponse()
    if respmsg.status == 200:
        result = respmsg.read()
        f = open(EDPubKeyFile,'w')
        f.write(result)
        f.close()
    else:
        sys.exit(104)
else:
    w.close()
#######################################
try:
    publickey = RSA.load_pub_key(EDPubKeyFile)
    decrypthardinfo = publickey.public_decrypt(data,RSA.pkcs1_padding)
except M2Crypto.RSA.RSAError:
    sys.exit(106)

hardinfolist = decrypthardinfo.split('/')

if hardinfolist[1] == realmaindisksn and hardinfolist[3] == realmainnicmac:
    sys.exit(100)
else:
    sys.exit(105)






