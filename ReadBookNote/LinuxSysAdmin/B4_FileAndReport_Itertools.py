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
    
#用生成器能达到同样效果
#**给iterator参数赋值为一个序列,在iter(iterator)后使其迭代化,变为一个迭代器***
#[1,4,6,4,1]是序列,而iter([1,4,6,4,1])是迭代器
#序列是数据结构存储数据的,而将其迭代化后其就具有迭代记忆功能了.能记住自己迭代到那个元素了.
"""
for i in iter([1,4,6,4,1]):
    print i
只是将iter([1,4,6,4,1]).next()动作自动化了.
"""

def dropwhile1(predicate,iterator):
    iterator = iter(iterator)
    for x in iterator:
        if not predicate(x):
            yield x
            break
    for x in iterator:
        yield x

generator_obj = dropwhile1(lambda x:x<5,[1,4,6,4,1])
print generator_obj.next()
print generator_obj.next()
print generator_obj.next()

#将上面的动作自动化
''' 
for el in dropwhile1(lambda x:x<5,[1,4,6,4,1]):
    print el # 6,4,1
'''

#-------------------------------------------

#-------iter--------------------------------
#Get an iterator from an object.  In the first form, the argument must
#supply its own iterator, or be a sequence.
i = iter('abcd')
print i.next()
print i.next()

s = {'one':1,'two':2,'three':3}
m = iter(s)
print m.next()
print m.next()
print m.next()
#---------------------------------------------

#------其它列表相关-----------------------------
import random

x = [random.randint(0,5) for i in range(20)]
print x  # [4, 0, 3, 2, 0, 3, 0, 2, 0, 4, 2, 0, 0, 5, 4, 4, 0, 3, 2, 3]

names = ['Dora\n', 'Ethan\n', 'Wesley\n', 'John\n', 'Anne\n','Mike\n', 'Chris\n', 'Sarah\n', 'Alex\n', 'Lizzie\n']

names = [name.strip() for name in names]

#默认按照字母序排序
names = sorted(names)

#sorted也可接受一个函数作为key参数,然后使用该函数排序,如函数len(),则按照len(each item)排序
names = sorted(names,key=len)

print names
#---------------------------------------------


    
    
    
    
    