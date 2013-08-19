# -*- encoding:utf-8 -*-
#!/usr/bin/env python

'''
Created on 2013-8-8

@author: root
'''
import sys
sys.path.append('./gen-py')

from hello import UserManager
from hello.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class UserManagerHandler():
    
    def __init__(self):
        pass
    
    # --
    # 如在thrift文件中void ping(),但在实际ping()下return有值,这样不可
    # 如在thrift文件中string ping(),但在实际ping()下没有return任何值，这样也不可.
    # 如上说明，必须严格按照thrift文件规定的设置参数和返回值
    # --
    
    def ping(self):
        return "hello world"
        print("Welcome to thrift....")
        
    def get_user(self,firstname,lastname):
        if firstname == "":
            raise UserException(1,'firstname is empty')
        if lastname == "":
            raise UserException(2,'lastname is empty')
        return lastname+" "+firstname+"!"
    

handler = UserManagerHandler()
processor = UserManager.Processor(handler)
transport = TSocket.TServerSocket(port=9090)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()
server = TServer.TSimpleServer(processor,transport,tfactory,pfactory)
print("starting the server.... ")
server.serve()
        


