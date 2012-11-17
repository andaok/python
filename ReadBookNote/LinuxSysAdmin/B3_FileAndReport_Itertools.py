# -*- encoding:utf-8 -*-

"""
itertools - Functional tools for creating and using iterators.
"""

import itertools

#chain将多个iterator合并成一个iterator
for i in itertools.chain([1,2,3],['a','b','c']):
    print i
    
#izip
for i in itertools.izip([1,2,3],['a','b','c']):
    print i