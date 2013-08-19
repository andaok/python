# -*- encoding:utf-8 -*-
#!/usr/bin/env python

'''
Created on 2013-8-4

@author: root
'''

import sys

sys.path.append("./gen-py")

from hello import *
from hello.ttypes import *

# -- Thrift File --
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

host = "127.0.0.1"
port = "9090"

try:
    # -- Init thrift connection and protocol handlers --
    transport = TSocket.TSocket(host,port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    
    agent = UserManager.Client(protocol)
    transport.open()
    
    print(agent.ping())
    
    print(agent.get_user("wye","jack"))

    transport.close()    
except Thrift.TException,tx:
    print "Something went wrong : %s"%(tx.message)
    
    