#!/usr/bin/env python
'''
Created on 2013-8-4

@author: root
'''

import sys
import os
import platform

host = "0.0.0.0"
port = 12345

sys.path.append('./gen-py')

from hello import *
from hello.ttypes import *


# -- Thrift File --
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class testHandler():
    def FileTransfer(self,filename,content):
        f = open(filename,"wb")
        f.write(content)
        f.close()
        return "1"
    
    def FileExists(self,filename):
        if os.path.isfile(filename):
            return True
        else:
            return False
        
    def GetSysVer(self):
        system_ver = platform.platform()
        if system_ver.find("el5") > 0:
            title = "5"
        elif system_ver.find("el6") > 0:
            title = "6"
        else:
            title = "Not Centos"
        return title 

handler = testHandler()
processor = hello.Processor(handler)
transport = TSocket.TServerSocket(host,port)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

server = TServer.TThreadedServer(processor,transport,tfactory,pfactory)

print("Start Server....")

server.serve()
