#!/usr/bin/env python
#-*- encoding:utf-8 -*-

"""
服务器程序使用循环来接受连接并发送回应，这相当于是一次最多处理一个客户端的请求，
这种方式通信效率很低
"""

import socket
import sys

host = "0.0.0.0"
port = 5006

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

try:
	s.bind((host,port))
except socket.error , msg:
	print("bind failed,error code : " + str(msg[0]) + "message" + msg[1])
	sys.exit()

print("socket bind complete")

s.listen(10)

print("socket now listening")

#now keep talking with the client
while 1:
	#wait to accept a connection - blocking call
	conn , addr = s.accept()
	print("connected with" + addr[0] + ":" + str(addr[1]))

	data = conn.recv(1024)
	print(data)
	reply = "ok..." + data

	if not data:
	    break

	conn.sendall(reply)

conn.close()
s.close()

 



