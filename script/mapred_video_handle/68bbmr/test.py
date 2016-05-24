import  baseclass

logger = baseclass.getlog("handlevideo")

'''
MapWebHdfs = baseclass.WebHadoop("10.2.10.14","50071","cloudiyadatauser",logger)


vid = "dirtest"

TmpDir_Path = "/tmp/%s" % vid
TmpHdfs_Path = "/%s" % vid

if MapWebHdfs.put_dir(TmpDir_Path,TmpHdfs_Path,overwrite="true"):
   print("success")
else:
   print("fail")
'''

import MySQLdb
import sys

def getStatus():
    try:
        dbconn = MySQLdb.connect(host="10.2.10.12",user="cloudiya",passwd="c10udiya")
        dbcursor = dbconn.cursor()
        dbconn.select_db('video1')
        sql = "select status from video where vid=%s"
        sql_result = dbcursor.execute(sql,"vXUekH2")
        status = dbcursor.fetchone()
        dbconn.commit()
        print(status)
    except Exception,e:
        print(e)
        sys.exit()

    print status[0]
    return status[0]
    
getStatus()



