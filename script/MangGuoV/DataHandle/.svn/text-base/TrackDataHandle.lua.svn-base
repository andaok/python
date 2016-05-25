                    
                     -- /
                     --   Real handle play data from tracking page
                     --   version 1.0 by wye
                     --   Copyright @ 2012 - 2013  Cloudiya Tech . Inc
                     -- /


                     local log_dict = ngx.shared.log_dict
                     local redis = require "resty.redis"
                     local cjson = require "cjson"

                     local red = redis:new()
                     red:set_timeout(1000)
                     local ok,err = red:connect("127.0.0.1",6379)
                     if not ok then
                        succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fail connect to local redis , Error info "..err)
                        return
                     end

                     -- Every play data,endlist,loadtable,playtable store in "redata" redis server
                     local redata = redis:new()
                     redata:set_timeout(1000)
                     local ok,err = redata:connect("10.2.10.19",6379)
                     if not ok then
                        succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fail connect to remote redis , Error info "..err)
                        return
                     end

 
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


                     -- Merger play segment of same play number
function MergerPlaySeg(oldlist)
   newlist = {}
   tmplist = {}

   for key,value in ipairs(oldlist) do
       k1 = value[1]
       k2 = value[2]
       v = value[3]
       if htgetn(tmplist) == 0 then
          tmplist = {k1,k2,v}
       else
          if tmplist[2] ~= k1 then
             table.insert(newlist,tmplist)
             tmplist = {k1,k2,v}
          else
             if tmplist[3] ~= v then
                table.insert(newlist,tmplist)
                tmplist = {k1,k2,v}
             else
                tmplist[2] = k2
             end
          end
       end
   end

   table.insert(newlist,tmplist)

   return newlist
end


                     -- Check key exists in the redis server
                     function CheckKey(redisname,keyname)
                              if redisname == "red" then
                                 local ok,err = red:exists(keyname)
                                 if not ok then
                                    succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--CheckKey--Fail connect to redis server :"..redisname.." ,Error info "..err)
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
                                    succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--CheckKey--Fail connect to redis server :"..redisname.." ,Error info "..err)
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
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--PlayLoadFail--Fail set to redis,Error info "..err)
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

                        --value["os"] = os
                        --value["browser"] = browser
                        value["ip"] = remoteip
                        --value["loadtime"] = time

                        -- Record client area information
                        if ngx.var.geoip_city_country_name then

                           value["country"] = ngx.var.geoip_city_country_code

                           --[[
                           if ngx.var.geoip_city_country_code == "CN" then 
                              value["region"] = ngx.var.geoip_region
                           elseif ngx.var.geoip_city_country_code == "HK" then 
                              value["region"] = "34" 
                           elseif ngx.var.geoip_city_country_code == "MO" then
                              value["region"] = "35"
                           elseif ngx.var.geoip_city_country_code == "TW" then
                              value["region"] = "36"
                           else      
                              value["region"] = "39"
                           end
                           --]]

                           value["city"] = ngx.var.geoip_city
                        else
                           -- For Debug
                           ---[[
                           value["country"] = "China"
                           value["region"] = "21"
                           value["city"] = "YinChuan"
                           --]]
                        end
                        
                        jsonvalue = cjson.encode(value)
                        local ok,err = red:set(key,jsonvalue)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--CheckFlow--Fail set to red,Error info "..err)
                           return
                        end
                        local ok,err = red:expire(key,129600)
                

                        -- Check user remian flow
                        ngx.print(1)

                     end
                   

                     -- Handle play video failure in first play
                     function PlayVideoFail(key,value)
                        --local time = os.time()
                    
                        value["starttime"] = value["wtime"]
                        jsonvalue = cjson.encode(value)
 
                        local ok,err = red:set(key,jsonvalue)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--PlayVideoFail--Fail set to redis,Error info "..err)
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
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--PlayVideoFail--Fail set to redis,Error info "..err)
                           return
                        end

                        a,b,vid,pid,flag = string.find(key,"(.*)_(.*)_(.*)")
                        red:zadd(vid.."_"..pid.."_set",tonumber(flag),jsonvalue)
                        local ok,err = red:expire(key,129600)

                     end

                    
                     -- / 
                     --
                     -- *********************************
                     -- Handle video play window close
                     -- *********************************
                     --
                     -- /

                     function PlayWindowClose(vid,pid,Cvalue,handleflag)

                        local ok,err = red:exists(vid.."_"..pid.."_".."set")
                        if not ok then
                            succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--CheckKey--Fail connect to redis server :".." red ".." ,Error info "..err)
                            return
                        elseif ok == 0 then
                            succ, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--CheckKey--Fail connect get the vid_pid_P,so it's not necessary to compute.:".." red "..",error info")
                            return
                        end

                        -- Obtain "loadtime,ip,os,browser,country,region,city" from "vid_pid_Y"
                        -- Obtain "starttime" from "vid_pid_0"
                        red:init_pipeline()
                        red:get(vid.."_"..pid.."_".."Y")
                        red:get(vid.."_"..pid.."_".."0")
                        local results,err = red:commit_pipeline()
                        if not results then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--PlayWindowClose--1--Fail get from redis pipeline,Error info "..err)
                           return
                        end                        
                        
                        -- "S" will be store in redis(redata) by keyname "vid_pid_S"
                        local S = cjson.decode(results[1])
                        S["starttime"] = cjson.decode(results[2])["starttime"]
                        
                        -- ########################
                        
                        
                        -- ########################
                        -- Obtain video meta information from redata , e.g Duration, avg bitrate every flow level.                        

                        duration = 74
            
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
                       
                        -- Client from ios platform 
                        if Cvalue["flag"] then
                           -- handle the ios platform.the data format is like this: {"playtime":34.54,"flag":"playing"}
                           for key,value in pairs(results) do
                               tvalue = value
                               
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
                                   iosnowplaytime = nowPlaytime
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

                                   elseif Playtime_reduce == 2 then
                                       
                                       ftmpnum = nowPlaytime                                       
                                   end

                               end
                            
                               -- Play pause
                               if tvalue["flag"] == "pause" then
                                  ftmpnum = tonumber(tvalue["playtime"])
                                  pausePlaytime = tonumber(tvalue["playtime"])
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

                            if iosnowplaytime then
                               --Ios platform closetime
                               closeplaytime = iosnowplaytime
                            else
                               --Common platform closetime
                               local res,err = red:get(vid.."_"..pid.."_P")
                               if res == ngx.null then
                                  succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Don't find key in redata")
                                  return
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
                        succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--periodlist is : "..vid.."_"..pid.."_"..cjson.encode(periodlist))
                        succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--lidlist is : "..vid.."_"..pid.."_"..cjson.encode(lidlist))
                        
                        --Correct the error data from the periodlist
                        tmplist = {}
                        for i,v in ipairs(periodlist) do
                            if tonumber(v[1]) > tonumber(v[2]) then
                               if tonumber(v[1]) > 2 then
                                  newvalue = tonumber(v[1])-2
                               elseif tonumber(v[1]) < 2 then
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

                        --Clear play segment of play number is 0 
                        for i,v in ipairs(SegmentFlagDict) do
                            if tonumber(v) ~= 0 then
                               ptmplist = {i,v}
                               table.insert(periodnumlist,ptmplist)
                            end           
                        end

                        ngx.say("periodnumlist is :",cjson.encode(periodnumlist))

                        --Play period data translate into a format for js draw
                        PlayPeriodData = {}
                        for i,v in ipairs(periodnumlist) do
                            tmplist = {tonumber(v[1])*2-2,tonumber(v[1])*2,tonumber(v[2])}
                            table.insert(PlayPeriodData,tmplist)
                        end

                        SortSegment = function(a,b) return a[1] < b[1] end
                        table.sort(PlayPeriodData,SortSegment)
                        
                        PlayPeriodData = MergerPlaySeg(PlayPeriodData)
                          
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
                        --Continue Structure S
                        S["comprate"] = comprate
                        S["periodata"] = cjson.encode(PlayPeriodData)
                       
                       redata:init_pipeline()
                      
                       --Write vid_pid_T to tracklist in redata and delete vid_pid_T in redata 
                       if handleflag == "close" then
                        servertime = os.time() 
                        redata:zadd("tracksortset",servertime,cjson.encode(S))
                        redata:del(vid.."_"..pid.."_".."T")
                       end

                       --Write vid_pid_T to redata and return vid_pid_T to js
                       if handleflag == "track" then
                          redata:set(vid.."_"..pid.."_".."T",cjson.encode(S))
                       end
                      
                        local results,err = redata:commit_pipeline()
                        if not results then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--PlayWindowClose--5--Fail set data to redata,Error info "..err)
                           return
                        end 

                        --####################### 
                        
                     end
                     -- ############################################################

                     -- Handle receive play information every 2 seconds
                     function RecPlayInfo(key,value)
                        jsonvalue = cjson.encode(value)
                        local ok,err = red:set(key,jsonvalue)
                        if not ok then
                            succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--RecPlayInfo--Fail set to redis,Error info "..err)
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
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--VStreamSwitch--Fail set to redis,Error info "..err)
                           return
                        end
                        local ok,err = red:expire(key,129600)
                     end

                     -- Handle video play error
                     function VideoPlayError(key,value)
                        jsonvalue = cjson.encode(value)

                        local ok,err = red:set(key,jsonvalue)
                        if not ok then
                           succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Fun--VideoPlayError--Fail set to redis,Error info "..err)
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
                     if htgetn(args) <= 4 then
                        
                         a,b,vid,pid,flag = string.find(args["key"],"(.*)_(.*)_(.*)")

                          if string.len(vid) == 7 and string.len(pid) == 4 then
                                                         
                             UserId = string.sub(vid,1,4)
                             FileId = string.sub(vid,5,-1)
                   
                             lua = "return "..args["value"]
                             local func = loadstring(lua)
                             tablevalue = func()
       
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
                                Now2Playtime = tonumber(tablevalue["playtime"])
                                
                                local res,err = red:get(vid.."_"..pid.."_K")
                                if res == ngx.null then
                                   Pre2Playtime = 0
                                else
                                   Pre2Playtime = tonumber(res)
                                end

                                local ok,err = red:set(vid.."_"..pid.."_K",Now2Playtime)
                                
                                if Now2Playtime-Pre2Playtime == 2 then
                                   if CheckKey("red",vid.."_"..pid.."_".."Y") and CheckKey("red",vid.."_"..pid.."_".."0")  then
                                      PlayWindowClose(vid,pid,tablevalue,"track")
                                   end
                                end

                             end

                             -- Video play window close
                             if flag == "C" then
                                RecPlayInfo(args["key"],tablevalue)
                                if CheckKey("red",vid.."_"..pid.."_".."Y") and CheckKey("red",vid.."_"..pid.."_".."0")  then
                                   PlayWindowClose(vid,pid,tablevalue,"close")
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
                                PlayVideoFail(args["key"],tablevalue) 
                             end

                             -- return tracking data to client
                             if flag == "T" then

                                if args["callback"] then
                                   callback = args["callback"]
                                   --ngx.header.content_type = "text/javascript"
                                end
                                
                                local res,err = redata:get(vid.."_"..pid.."_T")

                                if res == ngx.null then
                                   succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Don't find key in redata")

                                   local res1,err1 = red:get(vid.."_"..pid.."_Y")
                                   if res1 == ngx.null then
                                      ngx.say("ERROR")
                                   else
                                      if args["callback"] then
                                         ngx.say(callback.."("..res1..")")
                                      else
                                         ngx.say(res1)
                                      end
                                   end
                                else
                                   if args["callback"] then
                                         ngx.say(callback.."("..res..")")
                                   else
                                         ngx.say(res)
                                   end
                                end
                             end

                             -- If flag is "playing" ,Processed immediately.
                             if  tablevalue["flag"] == "playing" then
                                if CheckKey("red",vid.."_"..pid.."_".."Y") and CheckKey("red",vid.."_"..pid.."_".."0")  then
                                   PlayWindowClose(vid,pid,tablevalue,"track")
                                end   
                             end

                             -- If flag is "end" , Processed immediately.
                             if  tablevalue["flag"] == "end" then
                                 tablevalue["flag"] = nil 
                                 if CheckKey("red",vid.."_"..pid.."_".."Y") and CheckKey("red",vid.."_"..pid.."_".."0")  then
                                    PlayWindowClose(vid,pid,tablevalue,"track")
                                 end
                             end
                             
                          else
                             succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Main--"..args["key"].." data format is incorrect")
                             return
                          end                        
                           
                     else
                          succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Main--the number of parameters be less than or equal 4,but it is "..htgetn(args))
                          return
                     end

                     -- put redis connection to conn pool
                     local ok,err = red:set_keepalive(10,100)
                     if not ok then
                        succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Main--Fail to set red keepalive,error info : "..err)
                     end
                     local ok,err = redata:set_keepalive(10,100)
                     if not ok then
                        succ, err, forcible = log_dict:set(os.date("%x/%X"),"Track--Main--Fail to set redata keepalive,error info : "..err)
                     end


                                          
