#-*- encoding:utf-8 -*-

'''
Created on 2012-11-18

@author: root
'''

import xmlrpclib

def XMLRPCExample():
    x = xmlrpclib.ServerProxy('http://127.0.0.1:8765')

    print x.ls('.')

    print x.ls('/tmp/')

    print x.ls('/tmp/nodir')

    print x.ls_boom('/tmp/nopdir')

#################################

import Pyro.core

def PyroExample():
    psa = Pyro.core.getProxyForURI("PYROLOC://127.0.0.1:7766/psaexample")
    
    print psa.ls('/tmp')
    
    print psa.ls_boom("/tmp/nodir")
    
##################################

class PSACB():
    def __init__(self):
        self.some_attribute = 1
        
    def cb(self):
        return "PSA callback"

##################################
if __name__ == "__main__":

    #XMLRPCExample()
    #PyroExample()
    
    cb = PSACB()
    print "PYRO SECTION"
    PRINT "*"*20
    


