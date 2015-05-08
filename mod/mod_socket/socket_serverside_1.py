#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
服务器端一次处理多个连接
为了处理多个连接，我们需要一个独立的处理代码在主服务器接收到连接时运行。
一种方法是使用线程，服务器接收到连接然后创建一个线程来处理连接收发数据，然后主服务器程序返回去接收新的连接。
"""

import socket
import sys
from thread import *

host = "0.0.0.0"
port = 5006

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print("socket create")

#bind socket to local host and port
try:
    s.bind((host,port))
except socket.error, msg:
    print("bind failed,error code : " + str(msg[0]) + 'message' + msg[1])
    sys.exit()

print("socket bind complete")

#start listening on socket
#listen 函数所需的参数成为 backlog，用来控制程序忙时可保持等待状态的连接数。
#这里我们传递的是 10，意味着如果已经有 10 个连接在等待处理，那么第 11 个连接将会被拒绝。
s.listen(10)
print("socket now listening")

#function for handling connections,this will be used to create threads
def clientthread(conn):
    conn.send("welcome to the server,type something and hit enter\n")

    #infinite loop so that function do not terminate and thread do not end
    while True:

        #Receiving from client
        data = conn.recv(1024)
        reply = "ok..." + data

        if not data:
            break
         
        conn.sendall(reply)
    
    #came out of loop
    conn.close()

 #now keep talking with the client
while 1 :
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print("connected with " + addr[0] + ":" + str(addr[1])) 
    
    #start new thread takes 1st argument as a function name to be run,
    #second is the tuple of arguments to the function 
    start_new_thread(clientthread,(conn,))

s.close()