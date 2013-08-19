#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ---------------------------/
# pycurl示例6
# pycurl实现post方法上传文件到服务端
# ---------------------------/
# $_POST 无法解释二进制流，需要用到 $GLOBALS['HTTP_RAW_POST_DATA'] 或 php://input
# $GLOBALS['HTTP_RAW_POST_DATA'] 和 php://input 都不能用于 enctype=multipart/form-data
# ---------------------------/

# -- /
# 服务端wye.php代码
"""
<?php
$rawdata = file_get_contents("php://input");

echo $rawdata;

$fp = explode("\r\n",$rawdata);

$total = count($fp);

echo $total;

foreach($fp as $line)
{
  $tmp[] = $line;
}

print_r($tmp);

for($i=0;$i<$total;$i++)
 {
   if ($i == 0 || $i == 1 || $i == 2 || $i == $total-2)
    {
      echo $tmp[$i];
    } else {
           if (trim($tmp[$i]) <> '')
              {
                $savestr .= $tmp[$i]."\r\n";
              }

           }

 }

$fp = fopen("/tmp/kkk.jpg","w");
fwrite($fp,$savestr);
fclose($fp);
?>
"""
# -- /

import pycurl
import StringIO
import urllib

url = "http://graph.cloudiya.com/wye.php"

crl = pycurl.Curl()

values = [("image",(pycurl.FORM_FILE,"/var/data/github/BootStrap/html/tmp.jpg"))]
#values = [("image",(pycurl.FORM_FILE,"/var/data/github/BootStrap/html/tmp.png"))]
#values = [("html",(pycurl.FORM_FILE,"/var/data/github/BootStrap/html/demo1.html"))]

crl.setopt(pycurl.VERBOSE,1)
crl.setopt(pycurl.CONNECTTIMEOUT,60)
crl.setopt(pycurl.TIMEOUT,300)

crl.fp = StringIO.StringIO()
crl.setopt(pycurl.USERAGENT,"Wye Browser")

crl.setopt(crl.HTTPPOST,values)

crl.setopt(crl.URL,url)
crl.setopt(crl.WRITEFUNCTION,crl.fp.write)

headers = ["Content-Type: application/x-www-form-urlencoded"] 
crl.setopt(crl.HTTPHEADER,headers)

crl.perform()

print(crl.fp.getvalue()) 





