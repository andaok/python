# -*- encoding:utf-8 -*-

"""
itertools - Functional tools for creating and using iterators.
"""

from itertools import *

#-------chain-----------------------

#chain将多个iterator合并成一个iterator
for i in chain([1,2,3],['a','b','c']):
    print i
    

test = chain.from_iterable("abcdefg")
print test.next() # a
print test.next() # b

#借助生成器可达到同样的效果
def iterable(iterator):
    for i in iterator:
        yield i

test = iterable("abcdefg")
print test.next()
print test.next()

#--------------------------------------
    
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

#---------combinations--------------------
#combinations(iterable,r)
#创建一个迭代器,返回iterable中所有长度为r的子序列
test = combinations([1,2,3,4],2)
for item in test:
    print item
#-----------------------------------------

#-----------cycle-------------------------
#对iterator中的元素反复执行
i = 0
for el in cycle(['a','b','c','d','e']):
    i = i+1
    if i == 10:
        break
    print (i,el)
#------------------------------------------

#--------dropwhile-------------------------
#dropwhile(predicate,iterator)
#返回一个迭代器,只要函数predicate(item)为True,就丢弃iterator的项,如果函数predicate(item)为False,则返回该项及其后续所有项.
for el in dropwhile(lambda x:x<5,[1,4,6,4,1]):
    print el # 6,4,1

   

    
    
    
    
    
    