#!/usr/bin/env python
# -*- encoding:utf-8 -*-

'''
Created on may 9, 2013

@author: rli

Copyright @ 2011 - 2013  Cloudiya Tech . Inc 
'''

# add the webhdfs class

import pycurl
import StringIO
import os

class WebHadoop(object):
    '''
      WebHadoop 类是一个采用curl方式的hadoop集群的API接口
      初始话方式为：
       hdfs = WebHadoop("192.168.0.x","50071",username="yonghuming",loger)
       其中需要注意，在hadoop中需要开启hadoop的web接口。默认端口为50071.
       并且该机器能连接到后端的hadoop的datanode节点。因为在上传文件的时候需要访问后端节点。
       目前该类提供
       self.lsdir（）
       self.lsfile（）
       self.rename()
       self.remove()
       self.put_file()
       self.put_dir()
       self.checklink()
       self.mkdir()
      to do:
        self.append()

        
        
        AUTHOR :  LIRAN
        DATA : 2013-03-07
    '''
    def __init__(self,host,port,username,logger,prefix="/webhdfs/v1"):
        self.host = host
        self.port = port
        self.user = username
        self.logger = logger
        self.prefix = prefix
        self.status = None
        self.url = "http://%s:%s" % (host,port)
        self.url_path = self.url + self.prefix 


    def checklink(self):
        b = StringIO.StringIO()
        c = pycurl.Curl()
        checkurl = self.url + "/dfsnodelist.jsp?whatNodes=LIVE"        
        try:

            c.setopt(pycurl.URL, checkurl)
            c.setopt(pycurl.HTTPHEADER, ["Accept:"])
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)
            c.perform()
            self.status = c.getinfo(c.HTTP_CODE)
            body = b.getvalue()
            self.Write_Debug_Log(self.status,checkurl)
            p = re.compile(r'''Live Datanodes :(.*)</a''')
            results = p.findall(body)
            b.close()
            if results[0] == "0":
                self.logger.error("Sorry, There are not live datanodes in Hadoop Cluster!!!")
                self.curlObj.close()
                sys.exit(255)
            return results[0]
        except pycurl.error,e:
            self.logger.error("Sorry, can not get the hadoop http link .Erros: %s" % e)
            c.close()
            b.close()
            sys.exit(255)
        finally:
            c.close()
            b.close()
            
    
    def lsdir(self,path):
        put_str = '[{"op":LISTSTATUS}]'
        lsdir_url = self.url_path + path + "?op=LISTSTATUS"
        b = StringIO.StringIO()
        c = pycurl.Curl()
        try:
            c.setopt(pycurl.URL, lsdir_url)
            c.setopt(pycurl.HTTPHEADER, ["Accept:"])
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            body = b.getvalue()
            self.status = c.getinfo(pycurl.HTTP_CODE)
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
            #pass
        
        if self.status == 200:
            data_dir = eval(body)
            return data_dir['FileStatuses']['FileStatus']
            
        else:
            self.logger.error("Sorry,can not list the dir or file status!!!")
            self.Write_Debug_Log(self.status,lsdir_url)
            return []
        
             
    def lsfile(self,path):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        put_str = '[{"op":LISTSTATUS}]'
        lsdir_url = self.url_path + path + "?op=GETFILESTATUS"
        try:
            c.setopt(pycurl.URL, lsdir_url)
            c.setopt(pycurl.HTTPHEADER, ["Accept:"])
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            body = b.getvalue()
            self.status = c.getinfo(c.HTTP_CODE)
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
            
        if self.status == 200:
            data_dir = eval(body)
            if data_dir['FileStatus']['type'] == "DIRECTORY":
                self.logger.error("Sorry,this file %s is a dir actually!!!" % (path))
                return False
            else:
                return data_dir['FileStatus']
        else:
            self.logger.error("Sorry,can not list the dir or file status!!!")
            self.Write_Debug_Log(self.status,lsdir_url)
            return False
        
    def mkdir(self,path,permission="755"):
        b = StringIO.StringIO()
        c = pycurl.Curl()
        mkdir_str = '[{"op":"MKDIRS","permission"=permission}]'
        mkdir_url = "%s%s?op=MKDIRS&permission=%s" % (self.url_path,path,permission)        
        try:

            c.setopt(pycurl.URL, mkdir_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(mkdir_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"PUT")
            c.setopt(pycurl.POSTFIELDS,mkdir_str)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.perform()
            self.status = c.getinfo(c.HTTP_CODE)
            body = b.getvalue()
            b.close()
        except Exception,e:
            print e
        finally:
            c.close()
            
         
        if self.status == 200 :
            if "true" in body:
                self.logger.info("Great,Successfully Create dir %s in hadoop cluster!!" % (path))
                return True
            elif "false" in body:
                self.logger.info("Sorry,can't create this %s dir in hadoop cluster!!1!!")
                return False
            else:
                return False
        else:
            self.logger.error("Sorry,can't create this %s dir in hadoop cluster!!1" % (path))
            self.Write_Debug_Log(self.status,mkdir_url) 
                    

    def remove(self,path,recursive="True"):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        remove_str = '[{"op":"DELETE","recursive"=recursive}]'
        remvoe_url = "%s%s?op=DELETE&recursive=%s" % (self.url_path,path,recursive)        
        try:

            c.setopt(pycurl.URL, remvoe_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(remove_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"DELETE")
            c.setopt(pycurl.POSTFIELDS,remove_str)
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            body = b.getvalue()
            self.status = c.getinfo(c.HTTP_CODE) 
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
        if self.status == 200 :
            if "true" in body:
                self.logger.info("Great,Successfully delete dir or file %s in hadoop cluster!!" % (path))
                return True
            elif "false" in body:
                self.logger.info("Sorry,can't delete dir or file,maybe this dir is not exsited!!")
                return False
            else:
                return False
            
        else:
            self.logger.error("Sorry,can't create this %s dir in hadoop cluster!!1" % (path))
            self.Write_Debug_Log(self.status,remvoe_url)
            
    def rename(self,src,dst):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        rename_str = '[{"op":"RENAME"}]'
        rename_url = "%s%s?op=RENAME&destination=%s" % (self.url_path,src,dst)        
        try:

            c.setopt(pycurl.URL, rename_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(rename_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"PUT")
            c.setopt(pycurl.POSTFIELDS,rename_str)
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            body = b.getvalue()
            self.status = c.getinfo(c.HTTP_CODE)  
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
        if self.status == 200 :
            if "true" in body:
                self.logger.info("Great,Successfully rename dir or file %s in hadoop cluster!!" % (rename_url))
                return True
            elif "false" in body:
                self.logger.info("Sorry,can't rename dir or file,maybe this dir is not exsited!!")
                return False
            else:
                return False
            
        else:
            self.logger.error("Sorry,can't create this %s dir in hadoop cluster!!1" % (rename_url))
            self.Write_Debug_Log(self.status,rename_url)     

    def put_file(self,local_path,hdfs_path,overwrite="false",permission="755",buffersize="64"):
        c = pycurl.Curl()
        put_str = '[{"op":"CREATE","overwrite":overwrite,"permission":permission,"buffersize":buffersize}]'
        put_url = "%s%s?op=CREATE&overwrite=%s&permission=%s&buffersize=%s" % (self.url_path,hdfs_path,overwrite,permission,buffersize)        
        try:

            c.setopt(pycurl.URL, put_url)
            header_str = StringIO.StringIO()
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(put_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"PUT")
            c.setopt(pycurl.HEADER,1)
            c.setopt(pycurl.HEADERFUNCTION,header_str.write)
            c.setopt(pycurl.POSTFIELDS,put_str)
            b = StringIO.StringIO()
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,3600)
            c.setopt(pycurl.TIMEOUT,3600)            
            c.perform()
            redirect_url = c.getinfo(pycurl.EFFECTIVE_URL)
        except Exception,e:
            print e
        
        if os.path.isfile(local_path):
            try:
                f = file(local_path)
                filesize = os.path.getsize(local_path)
                c.setopt(pycurl.URL, redirect_url)
                c.setopt(pycurl.HEADER,1)
                c.setopt(pycurl.CUSTOMREQUEST,"PUT")
                c.setopt(pycurl.PUT,1)
                c.setopt(pycurl.INFILE,f)
                c.setopt(pycurl.INFILESIZE,filesize)
                c.setopt(pycurl.WRITEFUNCTION, b.write)
                c.setopt(pycurl.FOLLOWLOCATION, 1)
                c.setopt(pycurl.MAXREDIRS, 5)
                c.perform()
                print "yes.is ready to putting..."
                self.status = c.getinfo(c.HTTP_CODE)
                print b.getvalue()
            except Exception,e:
                print e
    	    finally:
                b.close()
                header_str.close()
                f.close()
        else:
            self.logger.error("Sorry,the %s is not existed,maybe it is not a file." % local_path)
            return False
        

        if self.status != 201:
            print self.status
            self.Write_Debug_Log(self.status,put_url)
            return False
        else:
            self.logger.info("Great,successfully put file into hdfs %s " % hdfs_path)
            return True

    def append(self,local_path,hdfs_path,buffersize=None):
        pass        
    
    def put_dir(self,local_dir,hdfs_path,overwrite="true",permission="755",buffersize="128"):
        dir_name = local_dir.split("/")[-1]
        if hdfs_path == "/":
            hdfs_path = hdfs_path + dir_name
            try:
                #self.mkdir(hdfs_path,permission):
                self.logger.info("Great,successful create %s hdfs_pash in hadoop." % hdfs_path)
            except Exception,e:
                print e
                self.logger.error("Sorry,create dir %s failure,errror" % hdfs_path)
                return False
            
        if os.path.isdir(local_dir):
            
            files = os.listdir(local_dir)
            print files
            for file in files:
                myfile = local_dir  + "/" + file
                put_file_path = hdfs_path + "/" + file
                if os.path.isfile(myfile):
                    self.put_file(myfile,put_file_path,overwrite,permission,buffersize)
                if os.path.isdir(myfile):
                    if self.mkdir(put_file_path,permission):
                        self.put_dir(myfile,put_file_path,overwrite,permission,buffersize)
                    else:
                        self.logger.error("Sorry,when putting dir to hadoop,can mkdir %s" % put_file_path)
                        return False
            return True
        else:
            self.logger.error("Sorry,local dir %s is not a directory." % local_dir)
            return False
        
    def get_file(self, local_path, hdfs_path,buffersize="128"):

        c = pycurl.Curl()
        f = file(local_path,'wb')
        get_str = '[{"op":"OPEN"}]'
        get_url = "%s%s?op=OPEN&buffersize=%s" % (self.url_path,hdfs_path,buffersize)        
        try:

            c.setopt(pycurl.URL, get_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(get_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"GET")
            f = file(local_path,'wb')
            c.setopt(pycurl.POSTFIELDS,get_str)
            c.setopt(pycurl.WRITEFUNCTION,f.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,3600)
            c.setopt(pycurl.TIMEOUT,3600)            
            c.perform()
            self.status = c.getinfo(pycurl.HTTP_CODE)
            

        except Exception,e:
            print e
        finally:
            c.close()
            f.close()

        if self.status != 200:

            self.Write_Debug_Log(self.status,get_str)
            return False
        else:
            self.logger.info("Great,successfully get file from hdfs %s " % hdfs_path)
            return True
        
    def get_dir(self,local_dir,hdfs_dir,buffersize="128"):
        dir_list = self.lsdir(hdfs_dir)
        
        if not os.path.isdir(local_dir):
            os.mkdir(local_dir)
            
        if self.status != 200:
            self.logger.error("Sorry,the hdfs_dir %s is not exsited.." % hdfs_dir)
            return False
        
        for x,y in enumerate(dir_list):
            hdfs_path = hdfs_dir
            local_path = local_dir
            if y['type'] == "FILE":
                file_path = local_path + "/" + y['pathSuffix']
                hdfs_path = hdfs_path + "/" + y['pathSuffix']
                self.get_file(file_path,hdfs_path)
                if self.status == 200:
                    self.logger.info("Great,Successful get file %s from hadoop cluster" % hdfs_path)
                else:
                    self.logger.error("Sorry,can not get file from %s " % hdfs_path)
            elif y['type'] == "DIRECTORY":
                print "local_dir_path is %s" % local_path
                dir_path = local_path + "/" + y['pathSuffix']
                hdfs_path = hdfs_path + "/" + y['pathSuffix']
                if not os.path.isdir(dir_path):
                    os.mkdir(dir_path)
                try:
                    self.get_dir(dir_path,hdfs_path)
                except Exception,e:
                    print e
            else:
                pass
        
        return True
        
    def cat_file(self, hdfs_path,buffersize="128"):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        put_str = '[{"op":"OPEN"}]'
        put_url = "%s%s?op=OPEN&buffersize=%s" % (self.url_path,hdfs_path,buffersize)        
        try:
            print "yes .ready to open"
            c.setopt(pycurl.URL, put_url)
            c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json','Content-Length: '+str(len(put_str))])
            c.setopt(pycurl.CUSTOMREQUEST,"GET")
    
            c.setopt(pycurl.POSTFIELDS,put_str)
            c.setopt(pycurl.WRITEFUNCTION,b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT,60)
            c.setopt(pycurl.TIMEOUT,300)            
            c.perform()
            
            self.status = c.getinfo(pycurl.HTTP_CODE)
            print b.getvalue()
        except Exception,e:
            print e
        finally:
            c.close()
            b.close()
    
        if self.status != 200:
            self.Write_Debug_Log(self.status,put_str)
            return False
        else:
            self.logger.info("Great,successfully put file into hdfs %s " % hdfs_path)
            return True
    
    def copy_in_hdfs(self,src,dst,overwrite="true",permission="755",buffersize="128"):
        tmpfile = "/tmp/copy_inhdfs_tmpfile"
        self.get_file(tmpfile,src)
        if self.status == 200:
            self.put_file(tmpfile,dst,overwrite="true")
            if self.status == 201:
                os.remove(tmpfile)
                return True
            else:
                os.remove(tmpfile)
                return False
        else:
            os.remove(tmpfile)
            return False 
           
    def Write_Debug_Log(self,status,url):
        if status != 200 or status != 201 :
            self.logger.error("Url : \"%s\" ,Exit code : %s"%(url,self.status))
            self.logger.error("fetch a error ,but don't quit")
