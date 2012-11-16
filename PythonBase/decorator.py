# -*- encoding:utf-8 -*-

'''
Created on Jul 24, 2012

@author: root
'''

from time import ctime,sleep

#@修饰符

def minus(f):
    print 'minus'
    f()

def plus(f):
    print 'plus'
    f()
    
def test(a):
    if a>3:
        return plus
    else:
        return minus

#解释器首先会解释@符号后面的代码，如果如上面的代码类似，
#那么test(5)将被执行，因为test参数5大于3，所以会返回一个函数指针plus（可以用C的这个名字来理解）
#plus将下一行的函数指针xxx当作参数传入，直到执行完成。最后结果将输出‘plus’和‘ok’。 

@test(5)
def xxx():
    print 'ok'
 
#minus因为本身已经是一个函数指针，所以会直接以xxx作为参数传入，结果会输出‘minus’和‘ok’。   
@minus
def yyy():
    print 'ok'
    
#@修饰符示例
#####1########
# decorator 仅调用tcfunc函数，该函数将foo作为一个参数，返回一个
# wrappedFunc函数对象，用该对象来取代foo函数在外部的调用，foo
# 定义的函数只能够在内部进行调用，外部无法获取其调用方式！！

def tcfunc(func):
    def wrappedfunc():
        print '[%s] %s called ' %(ctime(),func)
        return func()
    print "in tcfunc called"
    print "wrapped func %s"  %wrappedfunc
    return wrappedfunc

#@tcfunc则表示下面定义的函数将函数名作为tcfunc的参数被tcfunc调用。
@tcfunc
def foo():
    print "in foo called"
    pass

print "foo func : %s" %foo

foo()
print "-"*100
sleep(4)

for i in range(2):
    sleep(i)
    foo()
    print "-"*100

     
