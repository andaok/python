#!/usr/bin/env python

# -*- encoding:utf-8 -*-

'''
Created on Aug 28, 2012

@author: wye

Copyright @ 2011 - 2012 Cloudiya Tech. Inc.
'''

import os
import sys
import httplib
import libvirt
import optparse
import datetime
import subprocess
import socket
import fcntl
import struct
import time
import pickle
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

######################
#Get command input arguments
######################
cmdopt = optparse.OptionParser(description="import license file for this node",
                                                      prog="CloudiyaNodeAuth.py" ,
                                                      version="1.0",
                                                      usage="%prog --licensefile licensefilepath" )
cmdopt.add_option('-f','--licensefile',help="license file for this node")
options,arguments = cmdopt.parse_args()
cpuauthfile = options.licensefile.strip()

try:
    r = open(cpuauthfile,'rb')
except IOError:
    raise Exception("%s is not exist"%(cpuauthfile))
else:
    encryptcpuauthstring = r.read().decode("base64")

privatekey = RSA.load_key(cpuauthprikeyfile,lambda *args:"HFBVYUJKIHUTGHUYSAD")
decryptcpuauthstring = privatekey.private_decrypt(encryptcpuauthstring,RSA.pkcs1_padding)

decryptcpuauthlist = decryptcpuauthstring.split('_')

mainnicmac = decryptcpuauthlist[2]
maindisksn = decryptcpuauthlist[3]
serveryears = int(decryptcpuauthlist[5])

def getConnObj():
    connode = libvirt.open("qemu:///system")
    return connode

########################
#Parse physical cpu topology in this node
########################
def parseCPUTop():
    #test######
    #xmlfile="test.xml"
    #xmltree=ET.parse(xmlfile)
    #xmlroot=xmltree.getroot()
    ###########
      
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
        
##########################
#Obtain real hardware information in this node
##########################
# from python mailing list:
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

# from python mailing list:
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
        # exceptions are normal...
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
    raise Exception("Can't obtain MAC address for the first NIC")
                         
#print realmainnicmac

p=subprocess.Popen("sudo hdparm -I /dev/sda | grep 'Serial Number' | awk -F: '{print $2}'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
if p.stderr.read() == "":
    realmaindisksn = p.stdout.read().strip()
else:
    raise Exception("Can't obtain serial number for the main disk")

#print realmaindisksn

##########################
#To modify XML template based on the cpu authorization file
##########################
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

def modXMLTmp(cpuauthsum):
    cputoplist = parseCPUTop()
    cpuset = ""
    for i in range(0,cpuauthsum):
        cpuset = cpuset+","+cputoplist[i]["cpuid"]
    cpuset = cpuset[1:].strip()
    
    cloudXMLTmp = CloudiyaInsDir+"etc/workspace-control/libvirt_template.xml"
    xmltree=ET.parse(cloudXMLTmp)
    xmlroot=xmltree.getroot()
    vcpulist = xmlroot.findall("vcpu")
    vcpulist[0].set("cpuset","%s"%(cpuset))
    xmltree.write(cloudXMLTmp,"utf-8")

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

def getWSInfo(phycpunum,cpuauthsum,DeadlineDate):
    NodeHostName = getConnObj().getHostname()
    CpuAuthNum = cpuauthsum
    CpunAuthnum = phycpunum-cpuauthsum
    MemAuthMB = getNodeMemSum()
    MemunAuthMB = 0
    MainNicMac = mainnicmac
    MainDiskID = maindisksn
    ConnTime = time.ctime()
    dict = {"NodeHostName":NodeHostName,"CpuAuthNum":CpuAuthNum,"CpunAuthnum":CpunAuthnum,"MemAuthMB":MemAuthMB,"MemunAuthMB":MemunAuthMB,"MainNicMac":MainNicMac,"MainDiskID":MainDiskID,"ConnTime":ConnTime,"DeadlineDate":DeadlineDate.ctime()}
    return dict
    
def importAuthFile():
    now = time.strftime('%Y%m%d%H%M%S')
    cpuauthsn = decryptcpuauthlist[0]
    cpuauthnum = int(decryptcpuauthlist[4])
    mainnicmac = decryptcpuauthlist[2]
    maindisksn = decryptcpuauthlist[3]
    phycpunum = len(parseCPUTop())
    nowdate = datetime.datetime.now()
    try:
        r = open(cpuauthrefile,'r')
    except IOError:
        cpuauthsum = 0
        if cpuauthnum <= (phycpunum-cpuauthsum):
            #modify XML template
            cpuauthsum = cpuauthnum
            modXMLTmp(cpuauthsum)
            #get server deadline time
            deadlinedate = nowdate + datetime.timedelta(days=serveryears*365)
            #create cpuauthrefile file and write cpu authorization information to it
            cpuauthrelist = []
            cpuauthredict = {'cpuauthsn':cpuauthsn,'cpuauthnum':cpuauthnum,'cpuauthsum':cpuauthsum,'cpuauthtime':now,'deadlinedate':deadlinedate}
            cpuauthrelist.append(cpuauthredict)
            data = pickleData(cpuauthrelist)
            encryptDataToFile(data,cpuauthrepubkeyfile,cpuauthrefile)
            
            #update cpu authorization information in cloud platform control server
            info = getWSInfo(phycpunum,cpuauthsum,deadlinedate)
            try:
                message = sendInfoToWS(info,wshostname,wsport)
            except:
                statusmessage = "Failure"
            else:
                statusmessage = message
            
            #Print cpu authorization information
            print(""*10+"*"*50)
            print(" "*5+"Cloudiya Cloud CPU Authorization Succeeds!")
            print(""*10+"*"*50)
            print(""*10+"   Number of authorized CPUs by this license: %s"%(cpuauthnum))
            print(""*10+"             Total number of authorized CPUs: %s"%(cpuauthnum))
            print(" ")
            print(""*10+"                 Number of Unauthorized CPUs: %s"%(phycpunum-cpuauthnum))
            print(""*10+"                    Valid Subscription years: %s"%(serveryears))
            print(""*10+"         Connecting to Cloudiya Cloud server: %s"%(statusmessage))
            print(""*10+"*"*50)          
        else:
            print(""*10+"*"*30)
            print(""*10+"ERROR  : Number of authorized CPUs granted by this license is greater than the number of remaining unauthorized CPUs")
            print(""*10+"*"*30)
            raise SystemExit(102)
    else:
        r.close()
        serdata = decryptData(cpuauthreprikeyfile,cpuauthrefile)
        cpuauthrelist = unpickleData(serdata)
        ############################################################
        #Check whether the cpu authorization file has been imported
        ############################################################
        for dict in  cpuauthrelist:
            if dict["cpuauthsn"] ==  cpuauthsn:
                print(""*10+"*"*30)
                print(""*10+"ERROR  : This license file has been imported")
                print(""*10+"*"*30)
                raise SystemExit(103)
        ##############################################################
        cpuauthsum = cpuauthrelist[len(cpuauthrelist)-1]["cpuauthsum"]
        olddeadlinedate = cpuauthrelist[len(cpuauthrelist)-1]["deadlinedate"]
        
        #get server deadline time
        if (nowdate-olddeadlinedate).days >= 0:
            deadlinedate = nowdate + datetime.timedelta(days=serveryears*365)
        else:
            deadlinedate = olddeadlinedate + datetime.timedelta(days=serveryears*365)
            
        if cpuauthnum <= (phycpunum-cpuauthsum):
            cpuauthsum = cpuauthsum+cpuauthnum
            #modify XML template
            modXMLTmp(cpuauthsum)
            #write cpu authorization information to cpuauthrefile
            cpuauthredict = {'cpuauthsn':cpuauthsn,'cpuauthnum':cpuauthnum,'cpuauthsum':cpuauthsum,'cpuauthtime':now,'deadlinedate':deadlinedate}
            cpuauthrelist.append(cpuauthredict)
            #print cpuauthrelist
            data = pickleData(cpuauthrelist)
            encryptDataToFile(data,cpuauthrepubkeyfile,cpuauthrefile)
            
            #update cpu authorization information in cloud platform control server
            info = getWSInfo(phycpunum,cpuauthsum,deadlinedate)
            try:
                message = sendInfoToWS(info,wshostname,wsport)
            except:
                statusmessage = "Failure"
            else:
                statusmessage = message
            
            #Print cpu authorization information
            print(""*10+"*"*50)
            print(" "*5+"Cloudiya Cloud CPU Authorization Succeeds!")
            print(""*10+"*"*50)
            print(""*10+"   Number of authorized CPUs by this license: %s"%(cpuauthnum))
            print(""*10+"             Total number of authorized CPUs: %s"%(cpuauthsum))
            print(" ")
            print(""*10+"                 Number of Unauthorized CPUs: %s"%(phycpunum-cpuauthsum))
            print(""*10+"                    Valid Subscription years: %s"%(serveryears))
            print(""*10+"         Connecting to Cloudiya Cloud server: %s"%(statusmessage))  
            print(""*10+"*"*50)      
        else:
            print(""*10+"*"*30)
            print(""*10+"ERROR  : Number of authorized CPUs granted by this license is greater than the number of remaining unauthorized CPUs")
            print(""*10+"*"*30)
            raise SystemExit(102)
             
##########################
# Main
##########################
if __name__ == "__main__":
    if decryptcpuauthlist[1] == "YES":
        if realmainnicmac == mainnicmac and realmaindisksn == maindisksn:
            importAuthFile()
        else:
            print(""*10+"*"*30)
            print(""*10+"         ERROR  : Invaild Cloudiya Cloud licence file")
            print(""*10+"POSSIBLE REASON : Cloudiya Cloud licence file is only valid with the particular server with reported hardware!")
            print(""*10+"*"*30)
    else:
        importAuthFile()
    





