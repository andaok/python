#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
高级数据结构Counter
"""

from collections import Counter

"""
统计一个单词在给定的序列出现多少次
"""

li = ["Dog", "Cat", "Mouse", 42, "Dog", 42, "Cat", "Dog"]
a = Counter(li)
print a  #Counter({'Dog': 3, 42: 2, 'Cat': 2, 'Mouse': 1})

"""
统计序列中不同单词的数目
"""

print(len(set(li))) #4

#--------------------------------------#

li = ["Dog", "Cat", "Mouse","Dog","Cat", "Dog"]
a = Counter(li)
print a  #Counter({'Dog': 3, 'Cat': 2, 'Mouse': 1})

print "{0}:{1}".format(a.values(),a.keys()) #[1, 3, 2]:['Mouse', 'Dog', 'Cat']

print a.most_common(2)  #  列出前两个最普遍的元素[('Dog', 3), ('Cat', 2)] 

"""
字符串中出现频率最高的单词，并打印出来。
"""

import re
from collections import Counter
 
string = """   Lorem ipsum dolor sit amet, consectetur
    adipiscing elit. Nunc ut elit id mi ultricies
    adipiscing. Nulla facilisi. Praesent pulvinar,
    sapien vel feugiat vestibulum, nulla dui pretium orci,
    non ultricies elit lacus quis ante. Lorem ipsum dolor
    sit amet, consectetur adipiscing elit. Aliquam
    pretium ullamcorper urna quis iaculis. Etiam ac massa
    sed turpis tempor luctus. Curabitur sed nibh eu elit
    mollis congue. Praesent ipsum diam, consectetur vitae
    ornare a, aliquam a nunc. In id magna pellentesque
    tellus posuere adipiscing. Sed non mi metus, at lacinia
    augue. Sed magna nisi, ornare in mollis in, mollis
    sed nunc. Etiam at justo in leo congue mollis.
    Nullam in neque eget metus hendrerit scelerisque
    eu non enim. Ut malesuada lacus eu nulla bibendum
    id euismod urna sodales.  """
 
words = re.findall(r'\w+', string) #This finds words in the document

print words

lower_words = [word.lower() for word in words]

word_counts = Counter(lower_words)

print word_counts

