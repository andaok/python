# -*- encoding:utf-8 -*-

'''
Created on Sep 8, 2012

@author: root
'''
'''
related module : httplib
intro : how to post a soap message with python
'''
import httplib

SM_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
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
dict = {"NodeHostName":"terry1.cloudiya.com","age":102}

SoapMessage = SM_TEMPLATE%(dict)

try:
    conn = httplib.HTTPS("c03.cloudiya.com:8443")

    conn.putrequest("POST", "/wsrf/services/InfoServices?wsdl")


    conn.putheader("Host","c03.cloudiya.com")
    conn.putheader("User-Agent", "python test")
    conn.putheader("Content-type", "text/xml;charset=\"UTF-8\"")
    conn.putheader("Content-length", "%d"%len(SoapMessage))
    conn.putheader("SOAPAction", "\"\"")
    conn.endheaders()
    conn.send(SoapMessage)

    statuscode,statusmessage,header = conn.getreply()
    print statuscode
    print statusmessage
    print header

    print conn.getfile().read()
except:
    
    print "fail"
else:
    print "start"

print "end"




