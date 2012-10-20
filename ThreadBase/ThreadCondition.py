# -*- encoding:utf-8 -*-

'''
Created on Sep 19, 2012

@author: root

write by wye in clouidya
'''

import threading 
import time

#商品
product = None

#条件变量
con = threading.Condition()

#生产者方法
def produce():
    global product
    
    print "produce acquire lock...."
    if con.acquire():
        print "produce get lock..."
        while True:
            if product is None:
                print "produce...."
                product = "anything"
                
                #通知消费者,商品已经生产.
                con.notify()
                
            #等待通知
            con.wait()
            time.sleep(2)

#消费者方法
def consume():
    global product
    
    print "consume acquie lock..."
    if con.acquire():
        print "consume get lock..."
        while True:
            if product is not None:
                print "consume..."
                product = None
                
                #通知生产者,商品已经没了
                con.notify()
                
            #等待通知
            con.wait()
            time.sleep(2)

t1 = threading.Thread(target=produce)
t2 = threading.Thread(target=consume)

t1.start()
t2.start()


