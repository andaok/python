                    
                     -- /
                     --   Real handle play data from client
                     --   version 1.0 by wye
                     --   version 2.0 by rli
                     --   revise by wye
                     --
                     --   Copyright @ 2012 - 2013  Cloudiya Tech . Inc
                     -- /


                     local log_dict = ngx.shared.log_dict
                     local redis = require "resty.redis"
                     --local json = require "json"
                     local cjson = require "cjson"

                     local red = redis:new()
                     red:set_timeout(1000)
                     local ok,err = red:connect("127.0.0.1",6379)
                     if not ok then
                        succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fail connect to local redis , Error info "..err)
                        return
                     end

                     -- Every play data,endlist,loadtable,playtable store in "redata" redis server
                     local redata = redis:new()
                     redata:set_timeout(1000)
                     local ok,err = redata:connect("10.2.10.19",6379)
                     if not ok then
                        succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fail connect to remote redis , Error info "..err)
                        return
                     end

                     local bite_sep = 10
 

                     -- /
                     --
                     -- Global functions
                     --
                     -- /


                     -- Calculate the number of elements for table
                     function htgetn(hashtable)
                        local n = 0
                        for _,v in pairs(hashtable) do
                            n = n + 1
                        end
                        return n

                     end

-- Split string by delimiter 
function split(str,delimiter)

  local sub_str_table = {}

  while true do
     local s , e = string.find(str,"%"..delimiter)
     if s and e then
        sub_str = string.sub(str,1,e-1)
        table.insert(sub_str_table,sub_str)
        str = string.sub(str,e+1,-1)
     else
        if htgetn(sub_str_table) > 0 then
           table.insert(sub_str_table,str)
           return sub_str_table
        else
           return nil
        end

        break

     end
  end
end


-- /
--   GET VISITORS AREA INFORMATION
-- /
function GetGeoInfo()
    if ngx.var.geoip_city_country_name then
       country = ngx.var.geoip_city_country_code
       city = ngx.var.geoip_city
       region = ngx.var.geoip_city_country_code
       if ngx.var.geoip_city_country_code == "CN" then 
          regionindex = ngx.var.geoip_region
          region = ParseRegionName(tonumber(regionindex))
       elseif ngx.var.geoip_city_country_code == "HK" then 
          region = "HK"
          city = "HongKong" 
       elseif ngx.var.geoip_city_country_code == "MO" then
          region = "Macao"
          city = "Macao"
       elseif ngx.var.geoip_city_country_code == "TW" then
          region = "TW"
          city = "Taiwan"
       end
    else
       country = "unknown"
       region = "unknown"
       city = "unknown"
    end
    return country,region,city
end

-- /
--    USER CUSTOMIZED SERVICE ROUTING INTERFACE
-- /
function ServiceRouteInterface(vid,pid)
    uid = string.sub(vid,1,4)
    -- CUSTOM TEAL TIME USER INFORMATION 
    local ok,err = redata:sismember("custom_collinfo_uid_set",uid)
    if ok == 1 then
       RealHandleCollInfo(vid,uid,pid)
    end    
end

-- /
--   REAL HANDLE COLLECT'S USER INFORMATION
-- /
function RealHandleCollInfo(vid,uid,pid)    
    if CheckKey("redata",vid.."_"..pid.."_".."S") and CheckKey("redata",vid.."_"..pid.."_".."z1") then
       local res1,err = redata:get(vid.."_"..pid.."_S")
       local res2,err = redata:get(vid.."_"..pid.."_z1")
       if res1 ~= ngx.null and res2 ~= ngx.null then
          Stable = cjson.decode(res1)
          z1table = cjson.decode(res2)
          playtime = os.date("%Y%m%d",tonumber(Stable["starttime"]))
          z1table["playtime"] = Stable["starttime"]
          z1table["comprate"] = split(tonumber(Stable["comprate"])*100,".")[1].."%"
          country,region,city = GetGeoInfo()
          z1table["geo"] = country..","..region..","..city
          tjson = cjson.encode(z1table)
          local ok,err = redata:rpush(uid.."_collinfo_"..playtime,tjson)
          if not ok then
             succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--RealHandleCollInfo--Fail rpush to redata,Error info"..err)
             return
          end
          local ok,err = redata:expire(uid.."_collinfo_"..playtime,604800)
       end
    end
end


                     -- Check key exists in the redis server
                     function CheckKey(redisname,keyname)
                              if redisname == "red" then
                                 local ok,err = red:exists(keyname)
                                 if not ok then
                                    succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckKey--Fail connect to redis server :"..redisname.." ,Error info "..err)
                                    return false
                                 elseif ok == 0 then
                                    return false
                                 elseif ok == 1 then
                                    return true
                                 end                                
                              end
                              if redisname == "redata" then
                                 local ok,err = redata:exists(keyname)
                                 if not ok then
                                    succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckKey--Fail connect to redis server :"..redisname.." ,Error info "..err)
                                    return false
                                 elseif ok == 0 then
                                    return false
                                 elseif ok == 1 then
                                    return true
                                 end                                
                              end
                     end
                     
                     -- To parse user os and browser information from agent
                     function ParseOSandBrowser(agent)
                        -- OS
                        if string.find(agent,"Linux") then
                           os = "linux"
                        elseif string.find(agent,"Windows NT 5.0") or string.find(agent,"Windows 2000") then
                           os = "windows 2000"
                        elseif string.find(agent,"Windows NT 5.1") or string.find(agent,"Windows XP") then
                           os = "windows xp"
                        elseif string.find(agent,"Windows NT 5.2") then
                           os = "windows server 2003"
                        elseif string.find(agent,"Windows NT 6.0") then
                           os = "windows vista"
                        elseif string.find(agent,"Windows NT 6.1") then
                           os = "windows 7"
                        elseif string.find(agent,"Windows NT 6.2") then
                           os = "windows 8"
                        elseif string.find(agent,"Windows ME") then
                           os = "windows me"
                        elseif string.find(agent,"OpenBSD") then
                           os = "openbsd"
                        elseif string.find(agent,"SunOS") then
                           os = "sunos"
                        elseif string.find(agent,"iPhone") then
                           os = "iPhone"
                        elseif string.find(agent,"iPad") then
                           os = "iPad"
                        elseif string.find(agent,"iPod") then
                           os = "iPod"
                        elseif string.find(agent,"Mac_PowerPC") or string.find(agent,"Macintosh") then
                           os = "macos"
                        else
                           os = "Unknown"
                        end

                        -- Browser
                        if string.find(agent,".*Firefox/([.0-9]+)") then
                           _,_,ver = string.find(agent,".*Firefox/([.0-9]+)")
                           browser = "firefox "..ver
                        elseif string.find(agent,".*MSIE%s+([.0-9]+)") then
                           _,_,ver = string.find(agent,".*MSIE%s+([.0-9]+)")
                           browser = "msie "..ver
                        elseif string.find(agent,".*Chrome/([.0-9]+)") then
                           _,_,ver = string.find(agent,".*Chrome/([.0-9]+)")
                           browser = "chrome "..ver
                        elseif string.find(agent,".*Safari/([.0-9]+)") then
                           _,_,ver = string.find(agent,".*Safari/([.0-9]+)")
                           browser = "Safari "..ver
                        else
                           browser = "Unknown"
                        end

                        return os,browser
                     end

                     -- To parse user region name from region code
                     function ParseRegionName(regcode)
                        regname = {"Anhui","Zhejiang","Jiangxi","Jiangsu","Jilin","Qinghai","Fujian","Heilongjiang","Henan","Hebei",
                                   "Hunan","Hubei","Xinjiang","Xizang","Gansu","Guangxi","Guizhou","Liaoning","Neimenggu","Ningxia",
                                   "Beijing","Shanghai","Shanxi","Shangdong","Shaanxi","Tianjin","Yunnan","Guangdong","Hainan","Sichuan","Chongqing"}
                        return regname[tonumber(regcode)]
                     end
                     
                     -- Handle player load failure
                     function PlayerLoadFail(key,value)
                        local remoteip = ngx.var.remote_addr
                        local useragent = ngx.var.http_user_agent
                        local time = os.time() 
                        local os,browser = ParseOSandBrowser(useragent)

                        value["os"] = os
                        value["browser"] = browser
                        value["ip"] = remoteip
                        value["loadtime"] = time

                        jsonvalue = cjson.encode(value)
                                           
                        local ok,err = red:set(key,jsonvalue)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--PlayLoadFail--Fail set to redis,Error info "..err)
                           return
                        end
                        local ok,err = red:expire(key,129600)
                     end

                     -- Handle check user remaining flow
                     function CheckFlow(key,value,vid,pid,uplvalue)

                        -- Get client base information
                        local remoteip = ngx.var.http_x_forwarded_for
                        local useragent = ngx.var.http_user_agent
                        local time = os.time()
                        local os,browser = ParseOSandBrowser(useragent)

                        value["os"] = os
                        value["browser"] = browser
                        value["ip"] = remoteip
                        value["loadtime"] = time

                        -- Record client area information
                        if ngx.var.geoip_city_country_name then

                           value["country"] = ngx.var.geoip_city_country_code
                           value["city"] = ngx.var.geoip_city

                           if ngx.var.geoip_city_country_code == "CN" then 
                              value["region"] = ngx.var.geoip_region
                              if ngx.var.geoip_region == "13" then
                                 value["city"] = "unknown"
                              end
                           elseif ngx.var.geoip_city_country_code == "HK" then 
                              value["region"] = "34"
                              value["city"] = "Hong Kong" 
                           elseif ngx.var.geoip_city_country_code == "MO" then
                              value["region"] = "35"
                              value["city"] = "Macao"
                           elseif ngx.var.geoip_city_country_code == "TW" then
                              value["region"] = "36"
                              value["city"] = "Taiwan"
                           else      
                              value["region"] = "39"
                              value["city"] = "unknown"
                           end

                        else
					       value["country"] = "unknown"
					       value["region"] = "unknown"
					       value["city"] = "unknown"
                        end
                        
                        jsonvalue = cjson.encode(value)
                        local ok,err = red:set(key,jsonvalue)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckFlow--Fail set to red,Error info "..err)
                           return
                        end
                        local ok,err = red:expire(key,129600)

                        -- Player no playlist
                        if string.len(vid) == 7 then

                            -- Increase 1 to vid in loadtable in redata for statistics the video load numbers
                            local ok,err = redata:hincrby("loadtable",vid,1)
                            if not ok then
                                succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckFlow--Fail hincrby load to redata,Error info"..err)
                                return
                            end
                            
                            -- Statistics the video load numbers in the region
                            local ok,err = redata:hincrby("regiontable",vid..value["region"],1)
                            if not ok then
                                succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckFlow--Fail hincrby regintbale vid to redata,Error info"..err)
                                return
                            end
                          
                            -- Statistics the user load numbers in the region
                            UserId = string.sub(vid,1,4)
                            local ok,err = redata:hincrby("regiontable",UserId..value["region"],1)
                            if not ok then
                                succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckFlow--Fail hincrby to uid redata,Error info"..err)
                                return
                            end
                           
                            -- Record all the vid of loaded
                            local ok,err = redata:sadd("loadset",vid)
                            if not ok then
                                succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckFlow--Fail sadd  vid to redata,Error info"..err)
                                return
                            end
      
                        end

                        -- Player with playlist
                        if string.len(vid) == 6 then
                    
                           -- Client information write to every video in the playlist
                           red:init_pipeline() 
                           for i,v in pairs(uplvalue) do
                               KEY_Y = v.."_"..pid.."_Y"
                               red:set(KEY_Y,jsonvalue)
                               red:expire(KEY_Y,129600)
                           end
                           local results,err = red:commit_pipeline()
                           if not results then
                              succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckFlow--1--Fail get from redis pipeline,Error info "..err)
                              return
                           end

                           -- Statistics the video load numbers in the region
                           -- Statistics the user's video load numbers in the region
                           redata:init_pipeline()
                           for i,v in pairs(uplvalue) do
                               UserId = string.sub(v,1,4)
                               redata:hincrby("loadtable",v,1)
                               redata:hincrby("regiontable",v..value["region"],1)
                               redata:hincrby("regiontable",UserId..value["region"],1)
                               redata:sadd("loadset",v)
                           end
                           local results,err = redata:commit_pipeline()
                           if not results then
                              succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckFlow--1--Fail get from redis pipeline,Error info "..err)
                              return
                           end
      
                        end

                        -- Check user remian flow 
                        local res,err = redata:get(UserId.."_flow")
                        if res == ngx.null then
                            succ, err, forcible = log_dict:set(os.date("%x/%X"),"Func--CheckFlow--2--Don't find key in redata")
                        else
                           flowstatflag = tonumber(res)
                           ngx.print(flowstatflag)
                        end

                     end
                   

                     -- Handle play video failure in first play
                     function PlayVideoFail(key,value)
                        --local time = os.time()
                    
                        value["starttime"] = value["wtime"]
                        jsonvalue = cjson.encode(value)
 
                        local ok,err = red:set(key,jsonvalue)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--PlayVideoFail--Fail set to redis,Error info "..err)
                           return
                        end
                        local ok,err = red:expire(key,129600)
                     end

                     -- Handle play video success
                     function PlayVideoSuc(key,value)
                        --local time = os.time()

                        value["starttime"] = value["wtime"]
                        value["flag"] = "start"
                        jsonvalue = cjson.encode(value)
                        local ok,err = red:set(key,jsonvalue)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--PlayVideoFail--Fail set to redis,Error info "..err)
                           return
                        end

                        a,b,vid,pid,flag = string.find(key,"(.*)_(.*)_(.*)")
                        red:zadd(vid.."_"..pid.."_set",tonumber(flag),jsonvalue)
                        local ok,err = red:expire(key,129600)
                        local ok,err = red:expire(vid.."_"..pid.."_set",129600)
                        
                        --[[
                        -- Increase 1 to vid in playtable in redata for statistics the video play numbers
                        local ok,err = redata:hincrby("playtable",vid,1)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--PlayVideoSuc--Fail hincrby to redata,Error info"..err)
                           return
                        end
                        --]]

                        -- Write vid_pid to pendinglist in red for prepared to handle's vid_pid
                        local ok,err = red:rpush("pendinglist",vid.."_"..pid)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--PlayVideoSuc--Fail rpush to redata,Error info"..err)
                           return
                        end
                        
                        -- Remove vid from "loadset"
                        local ok,err = redata:srem("loadset",vid)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--PlayVideoSuc--Fail srem from redata,Error info"..err)
                           return
                        end

                     end

                    
                     -- / 
                     --
                     -- *********************************
                     -- Handle video play window close
                     -- *********************************
                     --
                     -- /

                     function PlayWindowClose(vid,pid,Cvalue)

                        local ok,err = red:exists(vid.."_"..pid.."_".."set")
                        if not ok then
                            succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckKey--Fail connect to redis server :".." red ".." ,Error info "..err)
                            return
                        elseif ok == 0 then
                            succ, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckKey--Fail connect get the vid_pid_P,so it's not necessary to compute.:".." red "..",error info")
                            return
                        end

                        -- Obtain "loadtime,ip,os,browser,country,region,city" from "vid_pid_Y"
                        -- Obtain "starttime" from "vid_pid_0"
                        red:init_pipeline()
                        red:get(vid.."_"..pid.."_".."Y")
                        red:get(vid.."_"..pid.."_".."0")
                        local results,err = red:commit_pipeline()
                        if not results then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--PlayWindowClose--1--Fail get from redis pipeline,Error info "..err)
                           return
                        end                        
                        
                        -- "S" will be store in redis(redata) by keyname "vid_pid_S"
                        local S = cjson.decode(results[1])
                        S["starttime"] = cjson.decode(results[2])["starttime"]
                        
                        -- ########################
                        
                        
                        -- ########################
                        -- Obtain video meta information from redata , e.g Duration, avg bitrate every flow level.                        
                        local ok,err = redata:exists(vid.."_info")
                        if not ok then
                            succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckKey--Fail connect to redis server :"..redisname.." ,Error info "..err)
                            flbit = {332,446,722,1782}
                            duration = 10000
                        elseif ok == 0 then
                            flbit = {332,446,722,1782}
                            duration = 10000
                        elseif ok == 1 then
                            flbit_str = redata:get(vid.."_info")
                            flbit_dir = cjson.decode(flbit_str)
                            flbit = {}
                                                       
                            if flbit_dir["duration"] then
                                duration = flbit_dir["duration"]
                            else
                                duration = 10000
                            end
                            if  flbit_dir["one"] then
                                table.insert(flbit,flbit_dir["one"])
                                table.insert(flbit,flbit_dir["one"])
                                table.insert(flbit,flbit_dir["one"])
                                table.insert(flbit,flbit_dir["one"])
                                table.insert(flbit,flbit_dir["one"])
                            end
                            if flbit_dir["two"] then
                                flbit[2] = flbit_dir["two"]
                                flbit[3] = flbit_dir["two"]
                                flbit[4] = flbit_dir["two"]
                                flbit[5] = flbit_dir["two"]
                            end 
                            if flbit_dir["three"] then 
                                flbit[3] = flbit_dir["three"]
                                flbit[4] = flbit_dir["three"]
                                flbit[5] = flbit_dir["three"]
                            end
                            if flbit_dir["four"] then
                                flbit[4] = flbit_dir["four"]
                                flbit[5] = flbit_dir["four"]
                            end
                            if flbit_dir["five"] then
                                flbit[5] = flbit_dir["five"]
                            end
                        end

                        redata:set("filbit_list",cjson.encode(flbit)) 
            
                        -- ########################
                        
                        -- ########################
                        -- "pauselist" store pause playtime,format is "{10,19,67,......}"
                        local pauselist = {}

                        -- "endsum" store number of play complete sum
                        local endsum = 0

                        -- "average comprate"                        
                        local comprate = 0

                        -- "periodnumlist" Stored repeatedly play segment,format is {{StartPlayTime,EndPlayTime,repeatnum},...},e.g {{[0,6,2],[8,12,1],[14,16,2],...}}
                        local periodnumlist = {}

                        -- "periodlist" store play segment data,format is {{PlayTime,OldTime},...},e.g {{0,13},{15,25},...}
                        local periodlist = {}

                        -- "lidlist" store video flow switch data,format is {{StartPlayTime,FlowLevel,EndPlayTime},...},e.g { {0,2,10},{11,3,18},...}
                        local lidlist = {}

                        -- Temporary data                        
                        local dtmplist = {}  
                        local ftmplist = {}
                        local flowlevel = 0 
                        local ftmpnum = 0
                        local nowPlaytime = 0
                        local pausePlaytime = 0                                                 
                        local wtime = 0

                        -- The judgment of received data(vid_pid_N) is what action trigger
                        -- "start" : the expressed start(and restart) play video
                        -- "drag"  : the expressed Click progress bar trigger
                        -- "pause" : the expressed Click pause button trigger
                        -- "end"   : the expressed video auto play complete
                        -- "switch": the expressed flow level switch trigger
                        
                        results = {}
                        the_date = red:zrange(vid.."_"..pid.."_set",0,-1)
                        for i,v in pairs(the_date) do
                            table.insert(results,cjson.decode(v))
                        end
                       
                        ngx.say(Cvalue["flag"])

                        -- Client from ios platform 
                        if Cvalue["flag"] then
                           -- handle the ios platform.the data format is like this: {"playtime":34.54,"flag":"playing"}
                           for key,value in pairs(results) do
                               tvalue = value

                               -- format playtime
                               ret_table = split(tvalue["playtime"],".")
                               if ret_table then
                                  if ret_table[1]%2 == 0 then
                                     tvalue["playtime"] = ret_table[1]
                                  else
                                     tvalue["playtime"] = ret_table[1]+1
                                  end 
                               end
                               
                               -- video start or restart play
                               if tvalue["flag"] == "start" then
                                  flowlevel = tonumber(tvalue["lid"])
                                  ftmplist = {tonumber(tvalue["playtime"]),flowlevel}
                                  dtmplist = {tonumber(tvalue["playtime"])}

                                  ftmpnum = tonumber(tvalue["playtime"])
                                  wtime = tonumber(tvalue["wtime"])
                               end

                               -- To determine whether there is drag every two seconds to send playtime
                               if tvalue["flag"] == "playing" then

                                   nowPlaytime = tonumber(tvalue["playtime"])
                                   ios_2s_playtime = nowPlaytime
                                   Playtime_reduce = nowPlaytime - tonumber(ftmpnum)
                                 
                                   ngx.say("nowplaytime_ftmpnum",nowPlaytime.."_"..ftmpnum)

                                   if Playtime_reduce > 2 then
                                       table.insert(ftmplist,ftmpnum+2)
                                       table.insert(lidlist,ftmplist)
                                       ftmplist = {nowPlaytime,flowlevel}
 
                                       table.insert(dtmplist,ftmpnum+2)
                                       table.insert(periodlist,dtmplist)

                                       dtmplist = {nowPlaytime}
                                       ftmpnum = nowPlaytime
                                       
                                       wtime = tonumber(tvalue["wtime"])

                                   elseif Playtime_reduce < 0 then
                                       table.insert(ftmplist,ftmpnum+2)
                                       table.insert(lidlist,ftmplist)
                                       ftmplist = {nowPlaytime,flowlevel}
 
                                       table.insert(dtmplist,ftmpnum+2)
                                       table.insert(periodlist,dtmplist)

                                       dtmplist = {nowPlaytime}
                                       ftmpnum = nowPlaytime

                                       wtime = tonumber(tvalue["wtime"])

                                   elseif Playtime_reduce >= 0 and Playtime_reduce < 2 and Playtime_reduce == 2 then
                                
                                       ftmpnum = nowPlaytime
                                   end

                               end
                            
                               -- Play pause
                               if tvalue["flag"] == "pause" then
                                  ftmpnum = tonumber(tvalue["playtime"])
                                  pausePlaytime = tonumber(tvalue["playtime"])
                                  ngx.say("pausetime is",pausePlaytime)
                               end
              
                               -- Switch the video in the playlist
                               if tvalue["flag"] == "switch" then
                                  
                                  if htgetn(dtmplist) ~= 0 and htgetn(ftmplist) ~= 0 then 
                                     table.insert(ftmplist,tonumber(tvalue["playtime"]))
                                     table.insert(lidlist,ftmplist)
                                  
                                     table.insert(dtmplist,tonumber(tvalue["playtime"]))
                                     table.insert(periodlist,dtmplist)
                               
                                     dtmplist = {}
                                     ftmplist = {}
                                  end

                               end

                               -- The end of the video 
                               if tvalue["flag"] == "end" then
                                  table.insert(ftmplist,tonumber(tvalue["playtime"]))
                                  table.insert(lidlist,ftmplist)

                                  table.insert(dtmplist,tonumber(tvalue["playtime"]))
                                  table.insert(periodlist,dtmplist)

                                  dtmplist = {}
                                  ftmplist = {}
                               end

                           end
                        
                        -- The client from common platform 
                        else
 
                          for key,value in pairs(results) do

                            tvalue = value
                            
                            --Post key format is vid_pid_N(0-10000),action is "start" 
                            if tvalue["flag"] == "start" then
                               flowlevel = tonumber(tvalue["lid"])
                               ftmplist = {tonumber(tvalue["playtime"]),flowlevel}
                               table.insert(dtmplist,tonumber(tvalue["playtime"]))

                               wtime = tonumber(tvalue["wtime"])     
                            end
                          
                            --Post key format is vid_pid_N(1-10000),action is "drag"
                            if tvalue["oldtime"] then
                               table.insert(ftmplist,tonumber(tvalue["oldtime"]))
                               table.insert(lidlist,ftmplist)
                               ftmplist = {tonumber(tvalue["playtime"]),tonumber(flowlevel)}

                               table.insert(dtmplist,tonumber(tvalue["oldtime"]))
                               table.insert(periodlist,dtmplist)
                               dtmplist = {tonumber(tvalue["playtime"])}

                               wtime = tonumber(tvalue["wtime"])
                            end
                            
                            --Post key format is vid_pid_N(1-10000),action is "pause"
                            if tvalue["flag"] == "pause" then
                               table.insert(pauselist,tonumber(tvalue["playtime"]))
                               pausePlaytime = tonumber(tvalue["playtime"])
                            end

                            --Post key format is vid_pid_LN(1-10000),action is "switch"
                            if htgetn(tvalue) == 3 and tvalue["lid"] then
                               flowlevel = tonumber(tvalue["lid"])
                               table.insert(ftmplist,tonumber(tvalue["playtime"]))
                               table.insert(lidlist,ftmplist)
                               ftmplist = {tonumber(tvalue["playtime"]),tonumber(flowlevel)}    
                            end 
                            
                            -- Switch the video in the playlist
                            if tvalue["flag"] == "switch" then

                               if htgetn(dtmplist) ~= 0 and htgetn(ftmplist) ~= 0 then
                                  table.insert(ftmplist,tonumber(tvalue["playtime"]))
                                  table.insert(lidlist,ftmplist)
                                  ftmplist = {}

                                  table.insert(dtmplist,tonumber(tvalue["playtime"]))
                                  table.insert(periodlist,dtmplist)
                                  dtmplist = {}
                               end
 
                            end
                            
                            --If post key format is vid_pid_N(1-10000),action is "end"
                            if tvalue["flag"] == "end" then
                               endsum = endsum + 1
                               
                               --table.insert(ftmplist,duration)
                               table.insert(ftmplist,tonumber(tvalue["playtime"]))
                               table.insert(lidlist,ftmplist)
                               ftmplist = {}
                              
                               --table.insert(dtmplist,duration)
                               table.insert(dtmplist,tonumber(tvalue["playtime"]))
                               table.insert(periodlist,dtmplist)
                               dtmplist = {} 
                            end
    
                          end
 
                        end                        

                        --If you are playing or pause,close the playback window
                        if htgetn(dtmplist) == 1 or htgetn(ftmplist) == 2 then

                            if Cvalue["flag"] then
                               --Ios platform closetime 
                               closeplaytime = ios_2s_playtime
                            else
                               --Common platform closetime

                               --[[
                               timediff = tonumber(Cvalue["wtime"]) - tonumber(wtime)                            
                               closeplaytime = dtmplist[1] + timediff

                               if closeplaytime > tonumber(duration) then
                                  if pausePlaytime > 0 then
                                     closeplaytime = pausePlaytime
                                  else
                                     closeplaytime = tonumber(duration)
                                  end
                               end
                               --]]

                               local res,err = red:get(vid.."_"..pid.."_P")
                               if res == ngx.null then
                                  closeplaytime = 0
                               else
                                  restable = cjson.decode(res)
                                  closeplaytime = tonumber(restable["playtime"])
                               end
                         
                            end

                            ngx.say("closeplaytime is :",closeplaytime)

                            table.insert(ftmplist,closeplaytime)
                            table.insert(lidlist,ftmplist)
                            ftmplist = {}

                            table.insert(dtmplist,closeplaytime)
                            table.insert(periodlist,dtmplist)
                            dtmplist = {} 
                        end

                        -- FOR DEBUG
                        ngx.say(" old periodlist is : ",cjson.encode(periodlist))
                        succ, err, forcible = log_dict:set(os.date("%x/%X"),"periodlist is : "..vid.."_"..pid.."_"..cjson.encode(periodlist))
                        succ, err, forcible = log_dict:set(os.date("%x/%X"),"lidlist is : "..vid.."_"..pid.."_"..cjson.encode(lidlist))
                        
                        --Correct the error data from the periodlist
                        tmplist = {}
                        for i,v in ipairs(periodlist) do
                            if tonumber(v[1]) > tonumber(v[2]) then
                               if tonumber(v[1]) > 10 then
                                  newvalue = tonumber(v[1])-10
                               elseif tonumber(v[1]) < 10 then
                                  newvalue = 0
                               end

                               tmplist = {newvalue,tonumber(v[2])}
                               
                               table.remove(periodlist,i)
                               table.insert(periodlist,tmplist)                               
                            end
                        end
                        
                        -- FOR DEBUG
                        ngx.say("new periodlist is : ",cjson.encode(periodlist))
                        ngx.say("lidlist is : ",cjson.encode(lidlist))
                        ngx.say("pauselist is : ",cjson.encode(pauselist))
                        ngx.say("endlist is : ",endsum)

                        -- ######################
                        
                       

                        --#######################
                        --Flow Statistics
                        local flowsum = 0  
                        for i,v in ipairs(lidlist) do
                            flowsum = flowsum + math.abs(tonumber(v[3])-tonumber(v[1]))*tonumber(flbit[tonumber(v[2])])  
                        end

                        ngx.say(flowsum)
                        --#######################
                        
                        --#######################
                        --Play Segment Statistics
                        function stoeven(num)
                          if num%2 ~= 0 then
                             num = num - 1
                          end
                          return num
                        end
                      
                        function etoeven(num)
                          if num%2 ~= 0 then 
                             num = num + 1   
                          end
                          return num
                        end


                        SegmentFlagDict = {}
                        for i=1,etoeven(duration)/2,1 do
                            SegmentFlagDict[i]=0
                        end 

 
                        for i,v in ipairs(periodlist) do
                            StartSegFlag=stoeven(tonumber(v[1]))/2 + 1
                            EndSegFlag=etoeven(tonumber(v[2]))/2
                            for j=StartSegFlag,EndSegFlag,1 do
                                if SegmentFlagDict[j] then
                                   SegmentFlagDict[j] = SegmentFlagDict[j] + 1
                                else
                                   SegmentFlagDict[j] = 0
                                end
                            end
                        end  
                        
                        ngx.say("SegmentFlagDict is :",cjson.encode(SegmentFlagDict))

                        --If the record does not exist 0-2 seconds,then add 0-2 seconds play records
                        if SegmentFlagDict[1] == 0 then
                           SegmentFlagDict[1] = 1
                        end

                        for i,v in ipairs(SegmentFlagDict) do
                            if tonumber(v) ~= 0 then
                               ptmplist = {i,v}
                               table.insert(periodnumlist,ptmplist)
                            end           
                        end

                        ngx.say("periodnumlist is :",cjson.encode(periodnumlist))
                        
                        --#######################

                        --#######################
                        --Calculate the completion rate

                        local timesum = htgetn(periodnumlist)*2

                        ngx.say("See time is : ",timesum)
                        
                        if timesum > tonumber(duration) then
                           comprate = 1
                        else
                           comprate = timesum/tonumber(duration)
                        end                        

                        ngx.say("A play complete rate is : ",comprate)
                        --#######################

                        --#######################
                        --Continue Structure S (vid_pid_S)
                        S["flow"] = flowsum/(8*1024)
                        S["comprate"] = comprate

                        --Write vid_pid_S and vid_pid_J to redata
                        J_len = htgetn(periodnumlist)
                        if J_len == 0 then
                            periodnumlist = {{1,1}}
                        end

                        redata:init_pipeline()
                        redata:set(vid.."_"..pid.."_".."S",cjson.encode(S))
                        redata:set(vid.."_"..pid.."_".."J",cjson.encode(periodnumlist))

                        local results,err = redata:commit_pipeline()
                        if not results then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--PlayWindowClose--5--Fail set data to redata,Error info "..err)
                           return
                        end 
                        local ok,err = red:expire(vid.."_"..pid.."_".."S",129600)
                        local ok,err = red:expire(vid.."_"..pid.."_".."J",129600)
                        --####################### 
                        
                        --If handle success,move vid_pid from pendinglist to endlist
                        ok,err = red:lrem("pendinglist",1,vid.."_"..pid)
                        if tonumber(ok) == 1 then
                           redata:rpush("endlist",vid.."_"..pid)
                        else
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--PlayWindowClose--6--Don't find the vid_pid in pendinglist,Error info")
                           return
                        end
                        
                        -- Increase 1 to vid in playtable in redata for statistics the video play numbers
                        local ok,err = redata:hincrby("playtable",vid,1)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--PlayWindowClose--Fail hincrby to redata,Error info"..err)
                           return
                        end

                     end
                     -- ############################################################

                     -- Handle receive play information every 10 seconds
                     function RecPlayInfo(key,value)
                        jsonvalue = cjson.encode(value)
                        local ok,err = red:set(key,jsonvalue)
                        if not ok then
                            succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--RecPlayInfo--Fail set to redis,Error info "..err)
                            return
                        end
                        local ok,err = red:expire(key,129600)
                     end

                     -- Handle video pause,drag,end
                     function VPauseDragEnd(key,value)

                        if value["lid"] then
                           value["flag"] = "start"
                        end                        
                        jsonvalue = cjson.encode(value)

                        a,b,vid,pid,flag = string.find(key,"(.*)_(.*)_(.*)")
                        red:zadd(vid.."_"..pid.."_set",tonumber(flag),jsonvalue)
                        local ok,err = red:expire(key,129600)
                     end                     

                     -- Handle video stream switch
                     function VStreamSwitch(key,value)
                        jsonvalue = cjson.encode(value)

                        a,b,vid,pid,flag = string.find(key,"(.*)_(.*)_(.*)")
                        Num = string.sub(flag,2)
                        local ok,err = red:zadd(vid.."_"..pid.."_set",tonumber(Num),jsonvalue)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--VStreamSwitch--Fail set to redis,Error info "..err)
                           return
                        end
                        local ok,err = red:expire(key,129600)
                     end

                     -- Handle video play error
                     function VideoPlayError(key,value)
                        jsonvalue = cjson.encode(value)

                        local ok,err = red:set(key,jsonvalue)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--VideoPlayError--Fail set to redis,Error info "..err)
                           return
                        end
                        local ok,err = red:expire(key,129600)
                     end


                     -- /
                     -- **********************************
                     --          Main Program
                     -- **********************************
                     -- /
 
                     
                     local args = ngx.req.get_uri_args()
                     if htgetn(args) == 2 then
                        
                         a,b,vid,pid,flag = string.find(args["key"],"(.*)_(.*)_(.*)")

                          -- The player with playlist
                          if string.len(vid) == 6 and string.len(pid) == 4 then
                        
                             UserId = string.sub(vid,1,4)
                             UserPid = vid

                             -- Serialize string into a table data structure
                             lua = "return "..args["value"]
                             local func = loadstring(lua)
                             tablevalue = func()
                            
                             -- Get the Upid information
                             local ok,err = redata:exists(UserPid.."_info")
                             if not ok then
                                 succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckKey--Fail connect to redis server :"..redisname.." ,Error info "..err)
                             elseif ok == 0 then
                                 succ, err, forcible = log_dict:set(os.date("%x/%X"),"Fun--CheckKey--Fail get the Upid "..UserPid.." from redis server :"..redisname.." ,Error info "..err)   
                             elseif ok == 1 then    
                                 UserPid_str = redata:get(UserPid.."_info")
                                 UserPid_table = cjson.decode(UserPid_str)
                             end

                             if htgetn(UserPid_table) == 0 then
                                 succ, err, forcible = log_dict:set(os.date("%x/%X"),"Main--"..UserPid.." is null.")
                                 return                                    
                             end 
                            
                             -- Check user flow
                             if flag == "Y" then
                                 CheckFlow(args["key"],tablevalue,vid,pid,UserPid_table)                                 
                             end

                             -- Video play window close
                             if flag == "C" then
                                for i,v in pairs(UserPid_table) do
                                     -- KEY_Y = v.."_"..pid.."_C"
                                     -- RecPlayInfo(KEY_Y,tablevalue)
                                     if CheckKey("red",v.."_"..pid.."_".."Y") and CheckKey("red",v.."_"..pid.."_".."0")  then
                                         PlayWindowClose(v,pid,tablevalue)
                                     end                                     
                                end                                
                             end
                          
                        
                          -- The player no playlist 
                          elseif string.len(vid) == 7 and string.len(pid) == 4 then
                                                         
                             UserId = string.sub(vid,1,4)
                             FileId = string.sub(vid,5,-1)
                   
                             lua = "return "..args["value"]
                             local func = loadstring(lua)
                             tablevalue = func()
       
                             redata:set("test_tablevalue",cjson.encode(tablevalue))

                             -- Do different according to the different flags 
                             -- Load player failure
                             if flag == "X" then
                                PlayerLoadFail(args["key"],tablevalue)
                             end
                             
                             -- Check user flow
                             if flag == "Y" then
                                CheckFlow(args["key"],tablevalue,vid,pid)
                             end

                             -- Play video failure in play start
                             if flag == "X0" then
                                PlayVideoFail(args["key"],tablevalue)
                             end

                             -- Play video success
                             if flag == "0" then
                                PlayVideoSuc(args["key"],tablevalue)
                             end
                          
                             -- Receive play information every 10 seconds
                             if flag == "P" then
                                RecPlayInfo(args["key"],tablevalue)
                             end

                             -- Video play window close
                             if flag == "C" then
                                RecPlayInfo(args["key"],tablevalue)
                                if CheckKey("red",vid.."_"..pid.."_".."Y") and CheckKey("red",vid.."_"..pid.."_".."0")  then
                                   PlayWindowClose(vid,pid,tablevalue)
                                   ServiceRouteInterface(vid,pid)
                                end
                             end

                             -- Video pause,drag and end 
                             if tonumber(flag) and tonumber(flag) >= 1 then
                                VPauseDragEnd(args["key"],tablevalue)
                             end

                             -- Video stream switch
                             if string.sub(flag,1,1) == "L" then
                                VStreamSwitch(args["key"],tablevalue)
                             end

                             -- Video play error during play
                             if string.sub(flag,1,1) == "X" and string.len(flag) > 1 then
                                VideoPlayError(args["key"],tablevalue) 
                             end
                 
                          else
                             succ, err, forcible = log_dict:set(os.date("%x/%X"),"Main--"..args["key"].." data format is incorrect")
                             return
                          end                        
                           
                     else
                          succ, err, forcible = log_dict:set(os.date("%x/%X"),"Main--the number of parameters be 2,but it is "..htgetn(args))
                          return
                     end

                     -- put redis connection to conn pool
                     local ok,err = red:set_keepalive(10,100)
                     if not ok then
                        succ, err, forcible = log_dict:set(os.date("%x/%X"),"Main--Fail to set red keepalive,error info : "..err)
                     end
                     local ok,err = redata:set_keepalive(10,100)
                     if not ok then
                        succ, err, forcible = log_dict:set(os.date("%x/%X"),"Main--Fail to set redata keepalive,error info : "..err)
                     end


                                          
