#!/usr/bin/env python
#-*- encoding:utf-8 -*-

'fileinput mod test'

import fileinput

try:
	for line in fileinput.input("info.txt"):
		line = line.strip()
		infolist = line.split()
		print("name : %s , domain : %s , camnum : %s"%(infolist[0],infolist[1],infolist[2]))
except Exception as e:
	print ("Exception : %s"%e)
finally:
	fileinput.close()



