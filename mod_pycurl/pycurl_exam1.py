#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ---------------------------/
# pycurl示例1
# ---------------------------/

import pycurl

Download_File = "/tmp/dl.jpg"
url = "http://192.168.0.111:88/html/tmp.jpg"

crl = pycurl.Curl()
crl.setopt(pycurl.URL,url)
crl.setopt(pycurl.FOLLOWLOCATION,1)

File_Handle = file(Download_File,"wb")
crl.setopt(pycurl.WRITEFUNCTION,File_Handle.write)
crl.perform()

Res_Code = crl.getinfo(crl.HTTP_CODE)

if Res_Code == 200:
    print("Download file success!!!")
elif Res_Code == 404:
    print("File not find!!!")
else:
    print("Unknow error")
    
File_Handle.close()
crl.close()
