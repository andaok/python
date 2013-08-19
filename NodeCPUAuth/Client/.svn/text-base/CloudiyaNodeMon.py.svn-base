#!/usr/bin/env python

# -*- encoding:utf-8 -*-

'''
Created on Aug 28, 2012

@author: wye

Copyright @ 2011 - 2012 Cloudiya Tech. Inc.
'''

import os
import sys
import random
import syslog
import libvirt
import socket
import fcntl
import struct
import time
import pickle
import httplib
import datetime
import subprocess
import ConfigParser
from M2Crypto import RSA
import xml.etree.ElementTree as ET

ABSPath = os.path.abspath(sys.argv[0])
CloudiyaInsDir = (os.path.dirname(ABSPath)).rstrip("bin")

configfile = CloudiyaInsDir+"etc/workspace-control/auth/auth.conf"
######################################
#Get static parameter form config file
######################################
config = ConfigParser.ConfigParser()
config.read(configfile)

cpuauthprikeyfile = CloudiyaInsDir+config.get("cpuauth", "cpuauthprikeyfile")
cpuauthrepubkeyfile = CloudiyaInsDir+config.get("cpuauth", "cpuauthrepubkeyfile")
cpuauthreprikeyfile = CloudiyaInsDir+config.get("cpuauth", "cpuauthreprikeyfile")
cpuauthrefile = CloudiyaInsDir+config.get("cpuauth", "cpuauthrefile")

wshostname = config.get("ws", "wshostname")
wsport = config.get("ws", "wsport")

#############################################
#Obtain real hardware information in this node
#############################################
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
        realmainnicmac = "NULL"

p=subprocess.Popen("sudo hdparm -I /dev/sda | grep 'Serial Number' | awk -F: '{print $2}'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
if p.stderr.read() == "":
    realmaindisksn = p.stdout.read().strip()
else:
    realmaindisksn = "NULL"

###############################################################
#                    CPU AUTH MONITOR
###############################################################
def getConnObj():
    connode = libvirt.open("qemu:///system")
    #connode = libvirt.open("qemu+ssh://root@192.168.0.108/system")
    return connode

def parseCPUTop():
    #test######
    #xmlfile="/var/data/python/LibvirtVm/Client/test.xml"
    #xmltree=ET.parse(xmlfile)
    #xmlroot=xmltree.getroot()
    ###########
    """
    Parse physical cpu topology in this node
    """
    connode = getConnObj()
    xmlstring = connode.getCapabilities()
    xmlroot=ET.fromstring(xmlstring)        
    cputopxmllist = xmlroot.findall("host/topology/cells/cell")
    phycpunum = len(cputopxmllist)
    cputoplist = []
    for cell in cputopxmllist:
        dict = {}
        dict['phycpusn'] = cell.get("id")
        cpulist = cell.findall("cpus/cpu")
        dict['cpucorenum'] = len(cpulist)
        cpuid = ""
        for cpu in cpulist:
            cpuid = cpuid+cpu.get("id")+","
        dict['cpuid'] = cpuid[0:-1].strip()
        cputoplist.append(dict)
    return cputoplist

def pickleData(data):
    serdata = pickle.dumps(data)
    return serdata

def unpickleData(serdata):
    data = pickle.loads(serdata)
    return data
    
def encryptDataToFile(data,key,file):
    publickey = RSA.load_pub_key(key)
    encryptCPUAuthString = publickey.public_encrypt(data,RSA.pkcs1_padding)
    encryptCPUAuthBase64 = encryptCPUAuthString.encode("base64")
    f = open(file,'w')
    f.write(encryptCPUAuthBase64)
    f.close()

def decryptData(key,file):
    f = open(file,'rb')
    encryptCPUAuthBase64 = f.read()
    f.close()
    encryptCPUAuthData = encryptCPUAuthBase64.decode("base64")
    privatekey = RSA.load_key(key,lambda *args:"HFBVYUJKIHUTGHUYSAD")
    decryptCPUAuthData = privatekey.private_decrypt(encryptCPUAuthData,RSA.pkcs1_padding)
    return decryptCPUAuthData

def getCPUAuthSum():
    """
	To obtain authorization CPU total number
	"""
    serdata = decryptData(cpuauthreprikeyfile,cpuauthrefile)
    cpuauthrelist = unpickleData(serdata)
    cpuauthsum = cpuauthrelist[len(cpuauthrelist)-1]["cpuauthsum"]
    return cpuauthsum

def getDeadlineDate():
    """
    To obtain server deadline date
    """
    serdata = decryptData(cpuauthreprikeyfile,cpuauthrefile)
    cpuauthrelist = unpickleData(serdata)
    deadlinedate = cpuauthrelist[len(cpuauthrelist)-1]["deadlinedate"]
    return deadlinedate.ctime()

def getAuthCPUSet(cpuauthsum):
    cputoplist = parseCPUTop()
    cpucoresum = len(cputoplist)*cputoplist[0]["cpucorenum"]
    cpumap = []
    for i in range(0,cpucoresum):
        cpumap.append(False)    
    cpuset = []
    for i in range(0,cpuauthsum):
        tmplist = cputoplist[i]["cpuid"].split(",")
        cpuset.extend(tmplist)
    for i in cpuset:
        cpumap[int(i)] = True
    return tuple(cpumap)

def getNodeMemSum():
    connode = getConnObj()
    memsum = 0
    xmlstring = connode.getSysinfo(0)
    xmlroot=ET.fromstring(xmlstring)
    memtopxmllist = xmlroot.findall("memory_device")

    for cell in memtopxmllist:
        entrylist =  cell.findall("entry")
        for entry in entrylist:
            if entry.get("name") == "size":
                memsum = int(entry.text[0:-2]) + memsum
    
    return memsum

def sendInfoToWS(info,wshostname,wsport):
    soap_mesg_struct = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope 
SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"  
xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Body>
<ns1:info xmlns:ns1="http://phonedirlux.homeip.net/types">
<symbol>%s</symbol>
</ns1:info>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""
    SoapMessage = soap_mesg_struct%(info)
    
    conn = httplib.HTTPS(wshostname+":"+wsport)
    conn.putrequest("POST", "/wsrf/services/InfoServices?wsdl")
    conn.putheader("Host",wshostname)
    conn.putheader("User-Agent", "FROM NODE")
    conn.putheader("Content-type", "text/xml;charset=\"UTF-8\"")
    conn.putheader("Content-length", "%d"%len(SoapMessage))
    conn.putheader("SOAPAction", "\"\"")
    conn.endheaders()
    conn.send(SoapMessage)

    statuscode,statusmessage,header = conn.getreply()    
    return statusmessage  

def getWSInfo(phycpunum,cpuauthsum):
    NodeHostName = getConnObj().getHostname()
    CpuAuthNum = cpuauthsum
    CpunAuthnum = phycpunum-cpuauthsum
    MemAuthMB = getNodeMemSum()
    MemunAuthMB = 0
    MainNicMac = realmainnicmac
    MainDiskID = realmaindisksn
    ConnTime = time.ctime()
    if cpuauthsum == 0:
        DeadlineDate = 0 
    else:
        DeadlineDate = getDeadlineDate()
    dict = {"NodeHostName":NodeHostName,"CpuAuthNum":CpuAuthNum,"CpunAuthnum":CpunAuthnum,"MemAuthMB":MemAuthMB,"MemunAuthMB":MemunAuthMB,"MainNicMac":MainNicMac,"MainDiskID":MainDiskID,"ConnTime":ConnTime,"DeadlineDate":DeadlineDate}
    return dict

def chkVcpuBindPerDom(cpuauthsum,wrkspname):
    """
    Check each virtual machine Vcpu bind situation
    """
    #Detection of virtual machine is a cloud platform to create    
    authvcpumap = getAuthCPUSet(cpuauthsum)
    connode = getConnObj()    
    if wrkspname.find("wrksp") == 0:
        dom = connode.lookupByName(wrkspname)
        tuple = dom.vcpus()
        vcpumaplist = tuple[1]
        for i in range(0,len(vcpumaplist)):
            if vcpumaplist[i] != authvcpumap:
                #Log
                syslog.openlog("CloudiyaAuth")
                syslog.syslog("Real AuthVcpuMap is %s"%(str(authvcpumap)))
                syslog.syslog("VM %s Vcpu %s VcpuMap is %s"%(wrkspname,i,vcpumaplist[i]))
                dom.pinVcpu(i,authvcpumap)
    
def scanVcpuBindSta(cpuauthsum):
    connode = getConnObj()
    if len(connode.listDomainsID()) > 0:
        for i in connode.listDomainsID():
            wrkspname = connode.lookupByID(i).name()
            chkVcpuBindPerDom(cpuauthsum,wrkspname)

import sys, os 

#####################################################################
#                        DAEMON
#####################################################################
def main():
    f = open("/dev/null","a+")
    os.dup2(f.fileno(),sys.stdout.fileno())
    os.dup2(f.fileno(),sys.stderr.fileno())
    syslog.openlog("CloudiyaAuth")
    while True:
        try:
            connode = libvirt.open("qemu:///system")
        except:
            syslog.syslog("Don't connecting to libvirt in this node")
        else:
            try:
                f = open(cpuauthrefile,"r")
            except IOError:
                syslog.syslog("No authorization records found")
                info = getWSInfo(len(parseCPUTop()),0)
                try:
                    message = sendInfoToWS(info,wshostname,wsport)
                except:
                    syslog.syslog("Connecting to Cloudiya Cloud server %s:%s failure"%(wshostname,wsport))    
            else:
                scanVcpuBindSta(getCPUAuthSum())
                info = getWSInfo(len(parseCPUTop()),getCPUAuthSum())
                try:
                    message = sendInfoToWS(info,wshostname,wsport)
                except:
                    syslog.syslog("Connecting to Cloudiya Cloud server %s:%s failure"%(wshostname,wsport))    
        time.sleep(900)
######################################################################                        
if __name__ == "__main__":
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit first parent
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)
    # decouple from parent environment
    os.chdir("/")
    os.setsid() 
    os.umask(0) 
    # do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit from second parent, print eventual PID before
            #print "Daemon PID %d" % pid 
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1) 
    # start the daemon main loop
    main() 



