#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
print(sys.version)


# -------------------
# 闭包示例，需在python3下运行。
# -------------------

def foo():

    x = 5

    def inner():

        nonlocal x
        x += 1
        return x
    return inner


p = foo()
print(p())
print(p())
print(p())


# ---------------------
# 请实现函数new_counter, 使得调用结果如下:
# c1 = new_counter(10)
# c2 = new_counter(20)
# print c1() , c2() , c1() ,c2()
# 输出: 11 21 12 22
# ---------------------

def bar(value):
	def inner():
		nonlocal value
		value += 1
		return value
	return inner

c1 = bar(10)
c2 = bar(20)

print(c1() , c2() , c1() ,c2())


# -------------------
# JUST TEST
# -------------------

def you(name):
	def inner():
		return "my name is %s"%name
	return inner

c3 = you("terry")
print(c3())

