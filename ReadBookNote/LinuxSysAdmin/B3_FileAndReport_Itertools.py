# -*- encoding:utf-8 -*-

"""
itertools - Functional tools for creating and using iterators.
"""

from itertools import *

#chain将多个iterator合并成一个iterator
for i in chain([1,2,3],['a','b','c']):
    print i
    
#izip将多个iterator迭代的内容混合成一个元组。
for i in izip([1,2,3],['a','b','c']):
    print i

#count
#count([n]) --> n, n+1, n+2, ...

#islice
# islice(seq, [start,] stop [, step]) --> elements from seq[start:stop:step]
print "by tens to 100"
for i in islice(count(),0,100,10):
    print i