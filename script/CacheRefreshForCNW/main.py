# -*- encoding:utf-8 -*-

# --/
#      主程序
#      获取待处理队列中数据,分类进行cache purge分别在squid和cdn
# --/

import sys
import redis
import public
from PurgeCache import exeCachePurge

logger = public.getLog("main")

#获取待处理队列中数据
redispool = redis.ConnectionPool(host=public.RedisIP,port=public.RedisPort,db=0)
redata = redis.Redis(connection_pool=redispool)
redpipe = redata.pipeline()
for i in xrange(public.PerHandleNum):
    redpipe.lpop(public.PendingHandleListName)
PathsList = redpipe.execute()

#规范及分离数据
PathsList_NoNone = [i for i in PathsList if i]

if len(PathsList_NoNone) == 0:
    logger.info("NO HAVE PATHS NEED TO PURGE")
    sys.exit()
else:
    FilePathsList = [i for i in PathsList_NoNone if "." in i]
    FilePathsList = [i for i in FilePathsList if "A0.xml" not in i and "A05.xml" not in i and "A0A.xml" not in i]
    DirPathsList = [i for i in PathsList_NoNone if "." not in i]

try:
    if len(FilePathsList) != 0:
        PurgeFilesObj =  exeCachePurge("file",FilePathsList)
        PurgeFilesObj.start()
    if  len(DirPathsList) != 0:
        PurgeDirsObj = exeCachePurge("dir",DirPathsList)
        PurgeDirsObj.start()
except Exception,e:
    logger.error("PURGE SQUID AND CDN EXECEPTION,%s"%e)    
    sys.exit()
