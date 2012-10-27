'''
Created on 2012-10-26

@author: root
'''

from subprocess import * 
import time
import sys,os

timeout = 1
list = {}

for i in range(4):
    p = Popen("ls -al /tmp > /dev/null",shell=True)
    list[i] = p
    
print list

for i in list:
    done = False
    while not done and timeout > 0:
        time.sleep(0.2)
        print "one is %s"%list[i].wait() 
        if list[i].wait() != -1:
            done = True
        timeout -=0.2
    if list[i].wait() != 0:
         sys.exit(list[i].wait())
    print list[i].wait() 
print "END"    
