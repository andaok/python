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

#------groupby--------------------------------

#itertools.groupby()函数接受一个序列和一个key函数, 并且返回一个生成二元组的迭代器。每一个二元组包含key_function(each item)的结果和另一个包含着所有共享这个key结果的元素的迭代器。
groups = groupby(names,len)

#调用list() 函数会“耗尽”这个迭代器, 也就是说 你生成了迭代器中所有元素才创造了这个列表。迭代器没有“重置”按钮。你一旦耗尽了它，你没法重新开始。如果你想要再循环一次(例如, 在接下去的for循环里面), 
#你得调用itertools.groupby()来创建一个新的迭代器
print list(groups)

#在这个例子里，给出一个已经按长度排序的名字列表, itertools.groupby(names, len)将会将所有的4个字母的名字放在一个迭代器里面，所有的5个字母的名字放在另一个迭代器里，以此类推。groupby()函数是完全通用的; 
#它可以将字符串按首字母，将数字按因子数目, 或者任何你能想到的key函数进行分组
groups = groupby(names,len)

for name_length,name_iter in groups:
    print "Names with %s letters:"%name_length
    for name in name_iter:
        print name

#注：itertools.groupby()只有当输入序列已经按分组函数排过序才能正常工作。在上面的例子里面，你用len() 函数分组了名字列表。这能工作是因为输入列表已经按长度排过序了
#----------------------------------------------

#------assert----------------------------------
assert 1+1 == 2
#assert 1+1 == 3

#assert 2+2 == 5,"Sum is Error value"
#----------------------------------------------

#-----迭代器列表化和字典化-------------------------
characters = ('S', 'M', 'E', 'D', 'O', 'N', 'R', 'Y')
guess = ('1', '2', '0', '3', '4', '5', '6', '7')

print tuple(zip(characters, guess))
print dict(zip(characters, guess)) 
#----------------------------------------------

#------字符串translate and maketrans------------
import string

#string.maketrans设置字符串转换规则表
#allchars = string.maketrans(",")  #所有字符串,不转换
#print allchars

atop = string.maketrans("e","a")  #建立"a"转为"a"的规则

s = "ahello python"
print s.translate(atop,'o')   #将"e"换为"a",同时删除"o"

#-------ifilter and ifilterfalse----------------------------------------
#创建一个迭代器，仅生成iterable中predicate(item)为True的项，如果predicate为None，将返回iterable中所有计算为True的项
print list(ifilter(lambda x:x%2,range(10)))
print list(ifilterfalse(lambda x:x%2,range(10)))

#----------------------------------------------

#------imap------------------------------------
#imap(function,iter1,iter2,iter3,....,itern)
d = imap(pow,(2,3,10),(5,2,3))
print tuple(d)
#-----------------------------------------------

#------permutations-----------------------------
#permutations(iterable[,r])
#创建一个迭代器，返回iterable中所有长度为r的项目序列，如果省略了r，那么序列的长度与iterable中的项目数量相同
print list(permutations('ABCD',2))
print list(permutations(range(3)))
#-----------------------------------------------

#------product-----------------------------------
print tuple(product('ABCD',"xy"))
print list(product(range(2),repeat=2))
print list(product(range(2),repeat=3))
#------------------------------------------------

#------repeat------------------------------------
#repeat(object,times=None)
print list(repeat(10,3))
#------------------------------------------------

#------takewhile---------------------------------
#创建一个迭代器，生成iterable中predicate(item)为True的项，只要predicate计算为False，迭代就会立即停止
print list(takewhile(lambda x:x<5,[1,4,6,4,1]))
#------------------------------------------------

#-------tee--------------------------------------
#tee(iterable[,n])
#从iterable克隆n个独立的迭代器，创建的迭代器以n元组的形式返回，n的默认值为2，此函数适用于任何可迭代的对象，但是，为了克隆原始迭代器，生成的项会被缓存，
#并在所有新创建的迭代器中使用，一定要注意，不要在调用tee()之后使用原始迭代器iterable，否则缓存机制可能无法正确工作。
#------------------------------------------------
    