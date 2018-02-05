#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
print(sys.version)


# --------------------
# 列表元素分组
# 比如列表[0,0,0,1,1,2,3,3,3,2,3,3,0,0]分割成[0,0,0],[1,1],[2],[3,3,3],[2],[3,3],[0,0]
# https://zhuanlan.zhihu.com/p/22067672
# --------------------

# 遍历

PengingSplitList = [0,0,0,1,1,2,3,3,3,2,3,3,0,0]

start = 0
end = 0

SplitedList = []

while end <= len(PengingSplitList) - 1:

    if PengingSplitList[start] == PengingSplitList[end]:
        end += 1
    else:
        SplitedList.append(PengingSplitList[start:end])
        start = end 
        end = end 

SplitedList.append(PengingSplitList[start:end])

print(SplitedList)

# 用itertools

from itertools import groupby

print [list(group) for _,group in groupby([0,0,0,1,1,2,3,3,3,2,3,3,0,0])]


# ---------------------
# 实现一个可迭代的类
# ---------------------


class yrange(object):

    def __init__(self,start=0,stop=0):

        self.start = start
        self.stop = stop

    def __iter__(self):

        return self

    def next(self):

        if self.start < self.stop:
            start = self.start
            self.start += 1
            return start
        else:
            raise StopIteration


for i in yrange(5,9):
    print " i is %s"%i


# ---------------------
# 请实现函数new_counter, 使得调用结果如下:
# c1 = new_counter(10)
# c2 = new_counter(20)
# print c1() , c2() , c1() ,c2()
# 输出: 11 21 12 22
# ---------------------

# -- 由generator实现，不是很合规.

def new_counter(value):

    while value < 100:
        yield value
        value += 1

c1 = new_counter(10)
c2 = new_counter(20)
print c1.next() # 10
print c1.next() # 11
print c2.next() # 20
print c2.next() # 21


# 满足要求

class jac(object):

    def __init__(self,value):

        self.value = value

    def __call__(self):

        self.value += 1
        return self.value

c1 = jac(10)
c2 = jac(20)

print "print result is :"
print c1() , c2() , c1() , c2() 


# -- 满足要求(itwye:此例虽然实现要求，但不好，并不需要value_list的。看上例)

class foo(object):

    def __init__(self,value):

        self.value = value
        self.value_list = []

    def __call__(self):

        if len(self.value_list) == 0:
            self.value_list.append(self.value + 1)
            return self.value + 1
        else:
            self.value_list.sort()
            new_value = self.value_list[-1:][0] + 1
            self.value_list.append(new_value)
            return new_value


c1 = foo(10)
c2 = foo(20)

print c1() , c2() , c1() , c2() 


# -- 满足要求

def bar(value):

    value_list = []

    def wrapper():

        if len(value_list) == 0:
            value_list.append(value + 1)
            return value + 1
        else:
            value_list.sort()
            new_value = value_list[-1:][0] + 1
            value_list.append(new_value)
            return new_value

    return wrapper

c1 = bar(10)
c2 = bar(20)


print c1() , c2() , c1() , c2() , c1() , c2()


# -- 满足要求

def jack(value):

    tmp = [value]

    def wrapper():

        tmp[0] += 1
        return tmp[0]

    return wrapper

c1 = jack(10)
c2 = jack(20)

print "print result is :"
print c1() , c2() , c1() , c2() , c1() , c2()

# ---------------------
# JUST TEST
# ---------------------

dict1 = {"name":"terry","age":10}

print type(dict1.items())
print type(dict1.iteritems())

for key,value in dict1.iteritems():
    print key,value



         


