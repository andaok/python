# -*- encoding:utf-8 -*-

'''
Created on Apr 6, 2012

@author: rootpull me

'''

import sys
import os

__version__ = "0.1"

def PrintArgs():
    print("your input args is :")
    for i in sys.argv:
        print(i)
    print("\n\n the PYTHONPATH is :",sys.path,"\n")

#返回当前目录
#print(os.getcwd())

def  PrintMax(x,y):
    if x > y :
        return x
    else:
        return y

def main():
    print(PrintMax(8,6))

if __name__ == "__main__":
    print("this program is being run by itself")
    #自己运行则调用main()
    main()

    





