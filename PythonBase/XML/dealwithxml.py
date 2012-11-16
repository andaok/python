# -*- encoding:utf-8 -*-

'''
Created on May 28, 2012

@author: root
'''

#python处理xml文件基本操作

import xml.etree.ElementTree as ET

xmlfile="core-site.xml"
xmltree=ET.parse(xmlfile)

xmlroot=xmltree.getroot()

#取xml中元素值，以此类推。
print(xmlroot[0].tag+"----"+xmlroot[0].text)
print(xmlroot[0][0].tag+"----"+xmlroot[0][0].text)
print(xmlroot[0][1].tag+"----"+xmlroot[0][1].text)
print('*'*40)
print(xmlroot[1].tag+"----"+xmlroot[1].text)
print(xmlroot[1][0].tag+"----"+xmlroot[1][0].text)
print(xmlroot[1][1].tag+"----"+xmlroot[1][1].text)
print('*'*40)

#找寻元素值，因示例xml文件很特殊,有很多重复结构。
print(xmlroot.find('property/name').text)
print(xmlroot.find('property/name').text)

#找到特定元素，并为其赋值。
running = True
i=0
while running:
    if (xmlroot[i][0].text == "fs.checkpoint.dir"):
        xmlroot[i][1].text ="wyeshuonihao"
        xmltree.write("core-site.xml")
        running = False
    else:
        i=i+1
        









