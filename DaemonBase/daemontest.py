# -*- encoding:utf-8 -*-

'''
Created on Sep 3, 2012

@author: root
'''
import sys, os
import syslog

#在daemon下,文件必须采用绝对路径.
fileABSpath =  "/tmp/daemon-log"   

def main():
    """ A demo daemon main routine, write a datestamp to 
        /tmp/daemon-log every 10 seconds.
    """
    import time
    syslog.openlog("RecordTime")
    f = open(fileABSpath, "w")
    
    #将写到标准输出的数据重定向到/dev/null
    #f = file("/dev/null","a+")
    #os.dup2(f.fileno(), sys.stdout.fileno())
    
    while 1: 
        #在daemon下,日志信息需借助syslog写到messages或着其它日志文件.
        syslog.syslog("start record time.....")
        print >> sys.stdout , "start record time....."
        #print >> sys.stderr , "start record time too....."
        f.write('%s/n' % time.ctime(time.time())) 
        f.flush() 
        time.sleep(10) 
               
if __name__ == "__main__":
    # do the UNIX double-fork magic, see Stevens' "Advanced 
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit first parent
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)
    # decouple from parent environment
    os.chdir("/") 
    os.setsid() 
    os.umask(0) 
    # do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit from second parent, print eventual PID before
            print "Daemon PID %d" % pid 
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1) 
    # start the daemon main loop
    main() 
