
#-*- encoding:utf-8 -*-

import struct
import binascii
from asyncore import dispatcher
from asynchat import async_chat
import socket,asyncore,struct
from cStringIO import StringIO


PORT = 5006

class ChatSession(async_chat):

    def __init__(self,sock):

        async_chat.__init__(self,sock)
        self.set_terminator("\r\n")
        self.data = []


    def collect_incoming_data(self,data):

        print "Repr Data :" , repr(data)
        print "Ori Data : " , data
        print "Tra Data :"  , binascii.b2a_hex(data)
        
        
        f = StringIO(data)

        print "THE TCP PACKAGE 1 PART"
        oridata  = f.read(2)
        print "ORI DATA IS :", repr(oridata)
        undata = struct.unpack('<h', oridata)[0]
        print "UNPACK DATA IS :", undata
        print "---------------------------"

        print "THE TCP PACKAGE 2 PART"
        oridata  = f.read(2)
        print "ORI DATA IS :", repr(oridata)
        undata = struct.unpack('<h', oridata)[0]
        print "UNPACK DATA IS :", undata
        print "---------------------------"
        
        print "THE TCP PACKAGE 3 PART"
        oridata  = f.read(2)
        print "ORI DATA IS :", repr(oridata)
        undata = struct.unpack('<h', oridata)[0]
        print "UNPACK DATA IS :", undata
        print "---------------------------"
        
        print "THE TCP PACKAGE 4 PART"
        oridata  = f.read(2)
        print "ORI DATA IS :", repr(oridata)
        undata = struct.unpack('<h', oridata)[0]
        print "UNPACK DATA IS :", undata
        print "---------------------------"

        print "THE TCP PACKAGE 5 PART"
        oridata  = f.read(6)
        print "ORI DATA IS :", repr(oridata)
        undata = struct.unpack('<ih', oridata)[0]
        print "UNPACK DATA IS :", undata
        print "---------------------------"

        print "THE TCP PACKAGE 6 PART"
        oridata  = f.read(6)
        print "ORI DATA IS :", repr(oridata)
        undata = struct.unpack('<ih', oridata)[0]
        print "UNPACK DATA IS :", undata
        print "---------------------------"


        print "THE TCP PACKAGE 7 PART"
        oridata  = f.read(4)
        print "ORI DATA IS :", repr(oridata)
        undata = struct.unpack('<i', oridata)[0]
        print "UNPACK DATA IS :", undata
        print "---------------------------"

        print "THE TCP PACKAGE 8 PART"
        oridata  = f.read(4)
        print "ORI DATA IS :", repr(oridata)
        undata = struct.unpack('<i', oridata)[0]
        print "UNPACK DATA IS :", undata
        print "---------------------------"

        print "THE TCP PACKAGE 9 PART"
        oridata  = f.read(4)
        print "ORI DATA IS :", repr(oridata)
        undata = struct.unpack('<i', oridata)[0]
        print "UNPACK DATA IS :", undata
        print "---------------------------"

        print "THE TCP PACKAGE 10 PART"
        oridata  = f.read(4)
        print "ORI DATA IS :", repr(oridata)
        undata = struct.unpack('<I', oridata)[0]
        print "UNPACK DATA IS :", undata
        print "---------------------------"


        self.data.append(data)


    def found_terminator(self):
        line = ''.join(self.data)
        self.data = []
        print line



class ChatServer(dispatcher):

    def __init__(self,port):

        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('',port))
        self.listen(6)
        self.sessions = []


    def handle_accept(self):

        conn,addr = self.accept()
        self.sessions.append(ChatSession(conn))


if __name__ == "__main__":

    s = ChatServer(PORT)
    try:
        asyncore.loop()
    except keyboardInterrupt:
        print





