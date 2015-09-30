


import socket
import struct
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


sock.connect(('localhost', 5005))
import time

file_obj = open("/tmp/a3.png")
f = file_obj.read()

sock.send(f)

sock.close()

