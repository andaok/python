#!/usr/bin/python
# -*- encoding:utf-8 -*-


# class test1(object):
#     def __enter__(self):
#         print "this is __enter__()"
#         return "Foo"
#     def __exit__(self,type,value,trace):
#         print "this is __exit__()"

# print test1()

# with test1() as test1obj:
#      print "testobj is:",test1obj


class test(object):
    def __enter__(self):
        return self
    def __exit__(self,type,value,trace):
        print "type is:",type
        print "value is:",value
        print "trace is:",trace
    def do_something(self):
        bar = 1/0
        return bar+10
with test() as testobj:
    tval = 1 + "2"
    testobj.do_something()


# class test(object):
#     def __enter__(self):
#         return self
#     def __exit__(self,type,value,trace):
#         print "type is:",type
#         print "value is:",value
#         print "trace is:",trace
#     def do_something(self):
#         bar = 1/0
#         return bar+10
# with test() as testobj:
#     testobj.do_something()

