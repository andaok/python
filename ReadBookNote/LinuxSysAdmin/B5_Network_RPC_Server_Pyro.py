#-*- encoding:utf-8 -*-

'''
Created on 2012-11-18

@author: root
'''

#pyro

import Pyro
import os

from B5_Network_RPC_Client import PSACB

class PSAExample(Pyro.core.ObjBase):
    
    def ls(self,directory):
        try:
            return os.listdir(directory)
        except OSError:
            return []
    
    def ls_boom(self,directory):
        return os.listdir(directory)
    
    def cb(self,obj):
        print "OBJECT:",obj
        print "OBJECT.__class__",obj.__class__
        print obj.cb()
        
if __name__ == "__main__":
    Pyro.core.initServer()
    daemon=Pyro.core.Daemon()
    uri=daemon.connect(PSAExample(),"psaexample")
    
    print "the daemon runs on port:",daemon.port
    print "the object's uri is:",uri
    daemon.requestLoop()


