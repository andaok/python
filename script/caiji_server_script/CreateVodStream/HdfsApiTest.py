from WebHDFSApi import WebHadoop
import logging
import logging.handlers

def getLog(logflag,loglevel="debug"):
    logger = logging.Logger(logflag)
    logfile = "/var/log/%s.log"%logflag
    hdlr = logging.handlers.RotatingFileHandler(logfile, maxBytes = 5*1024*1024, backupCount = 5)
    formatter = logging.Formatter("%(asctime)s -- [ %(name)s ] -- %(levelname)s -- %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)    
    if loglevel == "debug": 
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger

hosts = "10.2.0.8,10.2.0.10"

port = 14000

username = "cloudiyadatauser"


logger = getLog("GenVod")

WebHadoopObj = WebHadoop(hosts,port,username,logger)

#WebHadoopObj.put_file("/tmp/debug.txt","/vod/debug.txt")

print WebHadoopObj.mkdir("/kqvod/wyehaha")

