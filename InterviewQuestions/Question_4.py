#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
print(sys.version)

# ------------------
# 如何在排序数组中，找出给定数字出现次数.
# 如: {0,1,2,3,3,3,3,3,3,3,3,4,5,6,7,13,19}
# http://www.100mian.com/mianshi/python/13192.html
# ------------------



# ------------------
# 如何计算两个有序整形数组的交集
# 如： a=0,1,2,3,4 b=1,3,5,7,9
# http://www.100mian.com/mianshi/python/13192.html
# ------------------


# ------------------
# 模拟 C表达式 bool ? a : b
# ------------------


def choose(bool,a,b):

	return (bool and [a] or [b])[0]

print choose(1>2,5,6)
print choose(1<2,5,6)

