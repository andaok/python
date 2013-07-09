#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''
Created on JUN 25, 2013

@author: WYE
'''

import ujson
from operator import itemgetter,attrgetter,itruediv

# --/
#    背包算法1：
#    设有M种物品,每种物品都有一个重量及一个价值,同时有一背包,其容量为C,现在从M种物品里选取诺干件,
#    使其重量之和小于等于背包的容量,且价值和为最大.
#    
#    说明：
#    goodslist ： [[name,weight,value],...]
#    bpholdweight ： 背包可容纳的重量
# --/


def bpa1(goodslist,bpholdweight):
    
    newlistpool = [ [list[0],list[1],list[2],itruediv(list[2], list[1])] for list in goodslist]
    
    print(ujson.encode(newlistpool))
    
    sortlistpool = sorted(newlistpool,key=itemgetter(3),reverse=1)
    
    print(ujson.encode(sortlistpool))
    
    remholdweight = bpholdweight
    resultlist = []
            
    for name,weight,value,pervalue in sortlistpool:    
        if weight <= remholdweight:
            resultlist.append([name,weight,value,pervalue])
            remholdweight = remholdweight - weight

    print(ujson.encode(resultlist))


# --/
#    背包算法2：
#    设有M种物品,每种物品都有一个重量及一个价值,同时有一背包,其容量为C,现在从M种物品里选取诺干件,
#    使其重量之和刚好等于背包的容量,且价值和为最大.
#    
#    说明：
#    goodslist ： [[name,weight,value],...]
#    bpholdweight ： 背包可容纳的重量
# --/


def bpa2(goodslist,bpholdweight):
    
    name   = [list[0] for list in goodslist]
    weight = [list[1] for list in goodslist]
    value  = [list[2] for list in goodslist]
    
    n = len(goodslist)
    k = 0
    b = []
    r = []
    
    while True:
        while bpholdweight > 0 and k < n:
            if bpholdweight - weight[k] >= 0:
                b.append(k)
                bpholdweight -= weight[k]
            k += 1
            
        if bpholdweight == 0:
            r = [[name[x],weight[x],value[x]] for x in b]
            break
            
        if len(b) == 0:
            break
            
        k = b.pop()
        bpholdweight += weight[k]
        k += 1
            
    return r

def getMaxValue(goodslist,bpholdweight):
    
    list_len = len(goodslist)
    MaxValueList = []
    ValueSum = 0
    TheValueSum = 0
    
    for i in range(list_len):
        ReturnValList = bpa2(goodslist,bpholdweight)
        for list in ReturnValList:TheValueSum += list[2]
        if TheValueSum - ValueSum > 0:
            ValueSum = TheValueSum
            MaxValueList = ReturnValList
         
        goodslist = goodslist[1:]
        TheValueSum = 0      
                
    return MaxValueList

if __name__ == "__main__":
    
    # --/
    #    应用：
    #    用户空间装有许多视频文件,但未续费,需将用户空间降级为1G,但最大价值化保留几个视频文件
    #    使保留的这几个视频文件大小之和小于或等于1G,且视频播放次数之和最大
    #    数据说明：
    #    ["l123kop",450,90] ： 视频文件"l123kop"大小是450MB,播放次数是90次.
    # --/
    
    listpool = [["l123kop",450,90],["l123jkl",50,100],["l123mkl",10,800],["l123iop",76,79],["l123bgh",900,9000]]
    listpool1 = [["l123kop",1025,9000000],["l123jkl",1024,100],["l123mkl",1024,800],["l123iop",1024,79],["l123bgh",900,9000]]
    listpool2 = [["l123kop",1,1],["l123jkl",1,2],["l123mkl",2,2],["l123iop",4,10],["l123bgh",12,4],["l123bgh",6,3],["l123bgh",50,1000],["l123bgh",7,7]]
    
    bpa1(listpool2,18)
    
    # --/
    #    应用：
    #    出门远行,考虑带诺干物品,每种物品都有重量和自身的价值,背包可承重18KG.
    #    现在需要找到一种方案,使得装入背包的物品总重刚好等于18KG，且价值和为最大 
    #    数据说明：
    #    ["A",1,1] ： 物品"A"大小是1kg,价值权重为1.
    # --/
    
    List_Pool = [["A",1,1],["B",1,2],["C",2,2],["D",4,10],["E",12,4],["F",6,3],["G",50,1000],["H",7,7]] 
    
    bpGoodsList = getMaxValue(List_Pool,18)
    
    print(ujson.encode(bpGoodsList))  # [["B",1,2],["D",4,10],["F",6,3],["H",7,7]]
    