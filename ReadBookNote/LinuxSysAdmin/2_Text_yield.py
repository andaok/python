#-*- encoding:utf-8 -*-

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
c.next() 
c.next()

#send()可以传递yield表达式的值进去,而send()不能传递特定的值,只能传递None进去, c.send(none) == c.next()
#需要提醒的是，第一次调用时，请使用next()语句或是send(None)，不能使用send发送一个非None的值，否则会出错的，因为没有yield语句来接收这个值。

def w():
    print "hello"
    m = yield 5 
    print m
    d = yield 12
    print "how are you?"
    
c= w()
c.next()

c.send("JACK")