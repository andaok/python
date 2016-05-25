# -*- encoding:utf-8 -*-

'''
Purpose : deal with hadoop configuration file that are xml files

Usage : dealwithxml.py  xmlfile  xmlelement elementtext   

Created on May 28, 2012

@author: wye     
'''

import sys
import xml.etree.ElementTree as ET

xmlfile=sys.argv[1]
xmlelement=sys.argv[2]
elementtext=sys.argv[3]

xmltree=ET.parse(xmlfile)

xmlroot=xmltree.getroot()

running = True
i=0
while running:
    if (xmlroot[i][0].text == xmlelement ):
        xmlroot[i][1].text = elementtext
        xmltree.write(xmlfile)
        running = False
    else:
        i=i+1


