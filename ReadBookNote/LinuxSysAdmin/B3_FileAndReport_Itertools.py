# -*- encoding:utf-8 -*-

"""
itertools - Functional tools for creating and using iterators.
"""

from itertools import *

#chain将多个iterator合并成一个iterator
for i in chain([1,2,3],['a','b','c']):
    print i
    
#-------chain.from_iterable(iterables)--
test = chain.from_iterable("abcdefg")
print test.next()
print test.next()    

    
#izip将多个iterator迭代的内容混合成一个元组。
for i in izip([1,2,3],['a','b','c']):
    print i

#count
#count([n]) --> n, n+1, n+2, ...


#---------islice-----------------------

#islice(iterator, [start,] stop [, step]) --> elements from iterator[start:stop:step]
#islice类似于切片,把iterator按照规则分切返回一个迭代器
str = ""
for i in islice("abcdefg",0,4,1):
    str = str + i +","
print str.strip(",")   # a,b,c,d

str = ""
for i in islice("abcdefg",2,5,2):
    str = str + i +","
print str.strip(",")   # c,e

#count()为一迭代器 => 0,1,2,3.......
print "by tens to 100"
str=""
for i in islice(count(),0,100,10):
    str = str + "%s"%i +","
print str.strip(",")   # 0,10,20,30,40,50,60,70,80,90
    
#-----------------------------------------

   
    
    
    
    
    
    
    