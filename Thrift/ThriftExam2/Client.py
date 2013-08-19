# -*- encoding:utf-8 -*-
#!/usr/bin/env python

'''
Created on 2013-8-4

@author: root
'''

import sys
import platform

sys.path.append("./gen-py")

from hello import *
from hello.ttypes import *

# -- Thrift File --
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

host = "127.0.0.1"
port = "12345"

try:
    # -- Init thrift connection and protocol handlers --
    transport = TSocket.TSocket(host,port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    
    agent = hello.Client(protocol)
    transport.open()
    
    res = agent.FileExists("/tmp/xiha.txt")
    if res == True:
        print "True"
    else:
        print "False"
    
    # -- 定义服务端文件名和保存路径 --     
    filename = "/tmp/serverfile.txt"
    # -- 打开本地文件 --
    f = open("/tmp/clientfile.txt","rb")
    content = f.read()
    f.close()
    
    boolean = agent.FileTransfer(filename,content)
    
    res = agent.GetSysVer()
    print res

    transport.close()    
except Thrift.TException,tx:
    print "Something went wrong : %s"%(tx.message)
    
    