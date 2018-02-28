#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# 深复制与浅复制

def xcopy():

    import copy

    a = [1,2,3,4,["a","b"]]
    b = copy.copy(a)
    c = copy.deepcopy(a)

    a.append(5)
    a[4].append("c")

    print("a is %s"%a)
    print("b is %s"%b)
    print("c is %s"%c)

#xcopy()


# 实现个迭代器

class yrange(object):

    def __init__(self,start,end):
        self.start = start
        self.end = end

    def __iter__(self):
        return self

    def next(self):
        if self.start < self.end:
            start = self.start
            self.start = self.start + 1
            return start
        else:
            raise StopIteration

def use_yrange():

    for i in yrange(5,9):
        print("i value is %s"%i)

#use_yrange()

# 实现装饰器函数
from functools import wraps 
def def_call_num(func):
    call_num = [0]
    @wraps(func)
    def wrapper():
        call_num[0]+=1
        print("%s call num sum is %s"%(func.__name__,call_num[0]))
        return func()
    return wrapper

@def_call_num
def hello():
    print "hello world"

hello()
hello()
hello()

@def_call_num
def world():
    print "hello world"

world()
world()

# 实现类装饰器

class foo(object):
    def __init__(self,func):
        self.func = func
    def __call__(self):
        print("call start...")
        self.func()
        print("call end...")

@foo
def bar():
    print("hello bar")

bar()

# 闭包

def add_10():
    one = 10
    def wrapper(two):
        return one + two
    return wrapper

add1 = add_10()
print add1(10)
print add1(20)

# 生成器

genrator1 = (x for x in range(10))

print genrator1.next()
print genrator1.next()

# 生成器函数

def genrator2(start,stop):
    while start < stop:
        yield start
        start = start + 1

for i in genrator2(5,10):

    print i


# 字典

dict1 = {"name":"jack","age":10,"class":10}

for key,value in dict1.iteritems():

    print key , value


print dict1.get("sex","haha")


# 反射

class call_diff_func_by_arg(object):

    def __init__(self,arg):
        try:
            func = getattr(self,arg)
            func()
        except Exception,e:
            print(" don't find %s func"%arg)

    def hello(self):

        print("hello")

    def world(self):

        print("world")

call_diff_func_by_arg("hello")
call_diff_func_by_arg("world")


