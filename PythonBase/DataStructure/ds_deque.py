#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
高级数据结构deque
Deque是一种由队列结构扩展而来的双端队列(double-ended queue)，队列元素能够在队列两端添加或删除。
因此它还被称为头尾连接列表(head-tail linked list)，尽管叫这个名字的还有另一个特殊的数据结构实现。
Deque支持线程安全的，经过优化的append和pop操作，在队列两端的相关操作都能够达到近乎O(1)的时间复杂度。虽然list也支持类似的操作，
但是它是对定长列表的操作表现很不错，而当遇到pop(0)和insert(0, v)这样既改变了列表的长度又改变其元素位置的操作时，其复杂度就变为O(n)了
"""


import time
from collections import deque
 
num = 100000
 
def append(c):
    for i in range(num):
        c.append(i)
 
def appendleft(c):
    if isinstance(c, deque):
        for i in range(num):
            c.appendleft(i)
    else:
        for i in range(num):
            c.insert(0, i)
def pop(c):
    for i in range(num):
        c.pop()
 
def popleft(c):
    if isinstance(c, deque):
        for i in range(num):
            c.popleft()
    else:
        for i in range(num):
            c.pop(0)
 
for container in [deque, list]:
    for operation in [append, appendleft, pop, popleft]:
        c = container(range(num))
        start = time.time()
        operation(c)
        elapsed = time.time() - start
        print "Completed {0}/{1} in {2} seconds: {3} ops/sec".format(
              container.__name__, operation.__name__, elapsed, num / elapsed)