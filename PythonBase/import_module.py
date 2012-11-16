# -*- encoding:utf-8 -*-

'''
Created on Apr 6, 2012

@author: root
'''


#这将导入module_base所有模块成员，但不会导入__version__,因其以双下划线开头。
#from module_base import *

import module_base

def main():
  print("version is :",module_base.__version__)
#输出该模块包含的函数，类，变量等所有模块元素
  print(dir(module_base))
#列出当前模块元素
  print(dir())
#列出类str的元素或属性
  print(dir(str)) 

if __name__=="__main__":
    main()
