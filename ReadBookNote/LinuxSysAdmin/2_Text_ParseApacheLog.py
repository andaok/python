'''
Created on 2012-11-16

@author: root
'''

import sys

infile = open("File/access.log",'r')
for line in infile:
    print line.split()