'''
Created on 2013-8-17

@author: root
'''

import sys
import redis
import ujson
import time
import threading
import subprocess
from bottle import route,run,debug,request

pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
redata= redis.Redis(connection_pool=pool)    

def exeCmd(keyname):
    proc = subprocess.Popen(['iostat','-d','-k','1','10'],stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        redata.rpush(keyname,line.rstrip())

@route('/flushsquid',method="GET")
def flushSquid():
    prefix = request.query.jsoncallback
    keyname = "key"+str(request.query.key)
    try:
        tobj = threading.Thread(target=exeCmd,args=(keyname,))
        tobj.start()
        DataDict =  {'success':'1'}
    except Exception,e:
        DataDict = {'success':'0','text':e}
    return prefix+"("+ujson.encode(DataDict)+")"

@route('/getstdout',method="GET")
def getStdout ():
    prefix = request.query.jsoncallback
    keyname = "key"+str(request.query.key)
    line = redata.blpop(keyname,10)
    if line == None:
        DataDict = {"success":'0'}
    else:
        DataDict = {"success":'1','text':line[1]}
    return prefix+"("+ujson.encode(DataDict)+")"
    sys.exit()
    
run(host="0.0.0.0",port=8080,debug=True)
