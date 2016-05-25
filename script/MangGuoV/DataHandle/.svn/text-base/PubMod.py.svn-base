#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Created on Jan 9, 2013

@author: wye

Copyright @ 2012 - 2013  Cloudiya Tech . Inc 

"""

def mergerPlaySeg(oldlist):
    newlist = []
    tmplist = []
    
    for k1,k2,v in oldlist:
        if len(tmplist) == 0:
            tmplist = [k1,k2,v]
        else:
            if tmplist[1] != k1:
                newlist.append(tmplist)
                tmplist = [k1,k2,v]
            else:
                if tmplist[2] != v:
                    newlist.append(tmplist)
                    tmplist = [k1,k2,v]
                else:
                    tmplist[1] = k2
    
    newlist.append(tmplist)
    
    return newlist
