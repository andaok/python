#-*- encoding:utf-8 -*-

"""
Refer : http://www.cnblogs.com/coderzh/archive/2008/05/18/1202040.html
"""

def addlist(alist):
    for i in alist:
        yield i+1
        
alist = [1,2,3,4]
for x in addlist(alist):
    print x

#函数包含yield,意味着函数成为generator.

def h():
    print "hello world"
    yield 4
    print "nihao,world"
    yield 5
    
h()

c=h()
c.next()  # "hello world"
c.next()  # "nihao,world" ,不是"hello world " "nihao,world"

#yield的代码叠代能力不但能打断函数执行还能记下断点处的数据，下次next书接上回，这正是递归函数需要的。

#send()可以传递yield表达式的值进去,而next()不能传递特定的值,只能传递None进去, c.send(none) == c.next()
#需要提醒的是，第一次调用时，请使用next()语句或是send(None)，不能使用send发送一个非None的值，否则会出错的，因为没有yield语句来接收这个值。

def w():
    print "hello"
    m = yield 5 
    print m
    print "how are you?"
    yield 12
   
    
c= w()
m = c.next() 
print m

d = c.send("JACK")
print d

#实例
from StringIO import StringIO
conf_string = open("File/Apache.conf").read()
conf_file = StringIO(conf_string)

def yieldTest():
    for line in conf_file:
        yield line
        
#可以这么认为, yieldTest函数在加yield后变为迭代器了.      
       
print yieldTest().next()
print yieldTest().next()
print yieldTest().next()

for line in yieldTest():
    print line

#实例,做自己的迭代对象.
def myRange(r):
    i = 0
    while i < r:
        yield "%s\n"%i
        i = i+1
f = open("File/examfile.txt",'w')
f.writelines(myRange(10))
f.close()

#上例相等于下例
f = open("File/examfile1.txt","w")
f.writelines("%s\n"%i for i in range(10))
f.close()
        
#----生成器表达式-------------------------
#生成器表达式
w = ['E', 'D', 'M', 'O', 'N', 'S', 'R', 'Y']
gen = (ord(c) for c in w)
print gen
print gen.next()
print gen.next()

#使用yield实现上述
def ord_map(w):
    for i in w:
        yield ord(i)
gen = ord_map(w)
print gen.next()
print gen.next()

#生成器表达式功能相同但更紧凑
#---------------------------------------
