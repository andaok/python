
import ujson
import sys
import urllib2
import hashlib

class GlobalConfig():
    def __init__(self):
        self.redis_server_ip = "127.0.0.1"
        self.redis_server_port = 6379
        self.redis_db_name = 0 

class CDNFlush():
    
    def __init__(self):
        
        self.username = "xwu@cloudiya.com"
        self.key = "a6c9e10bb7da79e4b4a0fd170a48a656"
                
        self.flush_api_interface = "http://api.webluker.com/api/refresh/json/"
        self.check_api_interface = "http://api.webluker.com/api/getrefreshstatus/json/"
               
               
    def GetSign(self,params,key):
        Param_Pair_List = params.split("&")
        Param_Pair_List.sort()
        New_Params = ""
        for item in Param_Pair_List:
            New_Params = New_Params + item + "&"     
        sign = New_Params[:-1] + key
        MD5_Value = self.GetMD5(sign)
        return MD5_Value
    
    def GetMD5(self,str):
        hashobj = hashlib.md5(str)
        Bit32_MD5 = hashobj.hexdigest()
        return Bit32_MD5
    
    def SendPost(self,url,data):
        RetObj = urllib2.urlopen(url, data)
        return RetObj.read()

    def Flush(self,urls,rtype):
        params = "username=%s"%self.username+"&"+"rtype=%s"%rtype + "&" + "urls=%s"%urls
        params = params.encode("utf-8")
        sign = self.GetSign(params, self.key)
        params = params + "&sign=%s"%sign
        
        resp_data_json = self.SendPost(self.flush_api_interface,params)
        resp_data_dict = ujson.decode(resp_data_json)
        
        #print(resp_data_json)
        return  resp_data_dict
        
        if resp_data_dict["head"] == "fail":
            print(resp_data_dict["body"])
            sys.exit()
        else:
            url_rid_pairs_list = resp_data_dict["body"]
            rids = ""
            for item in url_rid_pairs_list:
                     for url,rid in item.items():
                         rids = str(rid) + "|" + rids
           
            self.rids = rids[:-1]             
            
            
    def Check(self,rids):
        params = "username=%s"%self.username + "&" + "rid=%s"%rids
        params = params.encode("utf-8")
        sign = self.GetSign(params, self.key)
        params = params + "&sign=%s"%sign
        
        resp_data_json = self.SendPost(self.check_api_interface,params)
        resp_data_dict = ujson.decode(resp_data_json)
        
        #print(resp_data_json)
        return resp_data_dict     
                

if __name__ == "__main__":
    
    #urls = "http://video.skygrande.com/test.html|http://video.skygrande.com/test1.html"
    urls = "http://video.skygrande.com/test/|http://video.skygrande.com/test1/test.html"
    rtype = 1
    
    FlushObj = CDNFlush()
    FlushObj.Flush(urls,rtype)
    #FlushObj.Check("9631212")




