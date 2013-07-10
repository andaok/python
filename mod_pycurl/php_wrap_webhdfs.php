<?php
/*
 * Created on Apr 20, 2012
 *
 * To change the template for this generated file go to
 * Window - Preferences - PHPeclipse - PHP - Code Templates
 */
 
 /*
  * 
  *  放置hdfs相关公用函数
  * 
  */
  
  require_once('publicvars.php');
  
  //警告提示信息模板
  function info($info) 
   {
       echo "<center><input type=\"text\" size=\"100\" name=\"info\" value=\"".$info."\" style=\"background:transparent;border:0; font-size:12px; font-weight:bold; text-align:center \"/></center>";
      //echo "<center><p style=\"background:transparent;border:0; font-size:12px; font-weight:bold; text-align:center \">".$info."</p></center>";
   }
   //---------------------------------------------------info end------------------------------------------------------------------//
   
 //上传文件到hdfs函数,只包含逻辑结构。
 function uploadtohdfs($hdfshost,$hdfsport,$localfilepath,$flowmediatype,$localfilename,$sfrewrite,$replinum,$defaultbuffersize,$defaultpermission) 
  {  
      if (checklink($hdfshost,$hdfsport)) 
      {
         //远端hdfs可连接，可上传文件.
         //检测流媒体类型文件夹是否存在。
         if (checkfolder($hdfshost,$hdfsport,$flowmediatype)) 
         {
                //流媒体类型文件夹存在，上传文件到该类型文件夹下
                //检测此流媒体类型下该文件是否存在
                if (checkfile($hdfshost,$hdfsport,$flowmediatype,$localfilename)) 
                {
                        if (transboolean($sfrewrite)) 
                        {
                                //文件存在且用户选择可覆盖，调用uploadfiletohdfs.
                                //提示文件正在上传
                                //info("Please Waiting ,Uploading ".$localfilename." ............");
                                if (uploadfiletohdfs($hdfshost,$hdfsport,$localfilepath,$flowmediatype,$localfilename,$sfrewrite,$replinum,$defaultbuffersize,$defaultpermission)) 
                                {
                                        info("文件".$localfilename."上传成功！");
                                        return 1;
                                } else {
                                        info("文件1".$localfilename."上传失败！");
                                        return 0;
                                }
                        } else {
                                //文件存在但用户选择不可覆盖，发警告信息。
                                info("流媒体类型库".$flowmediatype."下面已有一个同名文件".$localfilename."请选择其它文件上传！");
                                return 0;
                        }
                } else {
                        //此流媒体类型下该文件不存在，调用uploadfiletohdfs.
                   if (uploadfiletohdfs($hdfshost,$hdfsport,$localfilepath,$flowmediatype,$localfilename,$sfrewrite,$replinum,$defaultbuffersize,$defaultpermission)) 
                                {
                                        info("文件".$localfilename."上传成功！");
                                        return 1;
                                } else {
                                        info("文件2".$localfilename."上传失败！");
                                        return 0;
                                }
                 }
                
         } else {
                //流媒体类型文件夹不存在需创建。
                if(createfolder($hdfshost,$hdfsport,$flowmediatype,$defaultpermission)) 
                {
                        //上传文件到该流媒体类型下，调用uploadfiletohdfs.
                        if (uploadfiletohdfs($hdfshost,$hdfsport,$localfilepath,$flowmediatype,$localfilename,$sfrewrite,$replinum,$defaultbuffersize,$defaultpermission)) 
                                {
                                        info("文件".$localfilename."上传成功！");
                                        return 1;
                                } else {
                                        info("文件3".$localfilename."上传失败！");
                                        return 0;
                                }
                } else {
                   info("创建新流媒体类型文件夹".$flowmediatype."未成功！");
                   return 0;
                }
         }
      } else {
         //远端hdfs不可连接，打印警告信息。
         info("不能连接远端hdfs,无法上传流媒体文件！");
         return 0;
      }
  }
  //-----------------------------------------------uploadtohdfs end----------------------------------------------------------------//
  
  //检测是否可链接到远端hdfs
  function checklink($hdfshost,$hdfsport)
  {
        
        $url = "http://".$hdfshost.":".$hdfsport."/dfshealth.jsp";
        //print_r($url);
        $ch = curl_init();
        curl_setopt($ch,CURLOPT_URL,$url);
        curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
        curl_setopt($ch,CURLOPT_HEADER,1);
        $data = curl_exec($ch);
        curl_close($ch);
                
        if (eregi("HTTP/1.1 200 OK",$data)) 
        {
                return 1;
        } else {
                return 0;
        }       
  }
  //------------------------------------------------------------checklink end------------------------------------------------------------//
  
  //检测检测流媒体类型文件夹是否存在。
  function checkfolder($hdfshost,$hdfsport,$flowmediatype) 
  {
          $url = "http://".$hdfshost.":".$hdfsport."/webhdfs/v1/".$flowmediatype."?op=GETFILESTATUS";
          $ch = curl_init();
          curl_setopt($ch,CURLOPT_URL,$url);
          curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
          curl_setopt($ch,CURLOPT_HEADER,1);
          $data = curl_exec($ch);
          curl_close($ch);
          if (eregi("HTTP/1.1 200 OK",$data)) 
           {
                  return 1;
           } else {
                  return 0;
           }    
  }
  //-------------------------------------------------------------checkfolder end---------------------------------------------------------//
  
 //创建流媒体类型文件夹
 function createfolder($hdfshost,$hdfsport,$flowmediatype,$defaultpermission)
 {
        $url = "http://".$hdfshost.":".$hdfsport."/webhdfs/v1/".$flowmediatype."?op=MKDIRS&permission=".$defaultpermission;
        $ch = curl_init();
    curl_setopt($ch,CURLOPT_URL,$url);
    curl_setopt($ch,CURLOPT_PUT,1);
    curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
    curl_setopt($ch,CURLOPT_HEADER,1);
    $data = curl_exec($ch);
    curl_close($ch);
    if (eregi("HTTP/1.1 200 OK",$data)) 
          {
                 return 1;
          } else {
                 return 0;
          }     
 }
 //--------------------------------------------------------------createfolder end--------------------------------------------------------//
 
 //检测文件是否存在
 function checkfile($hdfshost,$hdfsport,$flowmediatype,$localfilename) 
 {
          $url = "http://".$hdfshost.":".$hdfsport."/webhdfs/v1/".$flowmediatype."/".$localfilename."?op=GETFILESTATUS";
          $ch = curl_init();
          curl_setopt($ch,CURLOPT_URL,$url);
          curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
          curl_setopt($ch,CURLOPT_HEADER,1);
          $data = curl_exec($ch);
          curl_close($ch);
          if (eregi("HTTP/1.1 200 OK",$data)) 
           {
                  return 1;
           } else {
                  return 0;
           }
 }
 //--------------------------------------------------------------checkfile end-------------------------------------------------------------//
 
 //-----------------test-------------------------//
 //uploadfiletohdfs($hdfshost,$hdfsport,"/tmp/upload/jisuankexuefazhanshi.flv","jiaoxue","jisuankexuefazhanshi.flv","false","3",$defaultbuffersize,$defaultpermission);
 //----------------------------------------------//

 
 //上传文件到hdfs,包含实际代码
 function uploadfiletohdfs($hdfshost,$hdfsport,$localfilepath,$flowmediatype,$localfilename,$sfrewrite,$replinum,$defaultbuffersize,$defaultpermission) 
 {
        //  第一步： 在hdfs端创建文件
        
        $url = "http://".$hdfshost.":".$hdfsport."/webhdfs/v1/".$flowmediatype."/".$localfilename."?op=CREATE";
        $url.= "&overwrite=".$sfrewrite."&replication=".$replinum."&permission=".$defaultpermission."&buffersize=".$defaultbuffersize;
        
        $ch = curl_init();
    curl_setopt($ch,CURLOPT_URL,$url);
    curl_setopt($ch,CURLOPT_PUT,1);
    curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
    curl_setopt($ch,CURLOPT_HEADER,1);
    $data = curl_exec($ch);
    curl_close($ch);
  
    $redirecturl = substr(strstr($data,"Location:"),strlen("Location:"),-strlen(strstr($data,"Content-Length")));
    
   // print_r($data);
   // print_r($redirecturl);
    
    // 第二步： 写数据到刚才创建的文件
  
    $fp = fopen($localfilepath,"rb");
    $filesize = filesize($localfilepath);
  
    $ch = curl_init();
    curl_setopt($ch,CURLOPT_URL,trim($redirecturl));
    curl_setopt($ch,CURLOPT_PUT,1);
    curl_setopt($ch,CURLOPT_INFILE,$fp);
    curl_setopt($ch,CURLOPT_INFILESIZE,$filesize);
  
    //返回结果写往变量，而不是输出到屏幕。
    curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
    //返回结果包含HTTPHEADER
    curl_setopt($ch,CURLOPT_HEADER,1);
    $data1 = curl_exec($ch);
   // print_r($data1);
    curl_close($ch);
    fclose($fp);
    
    if (eregi("HTTP/1.1 201 Created",$data1)) 
           {
                  return 1;
           } else {
                  return 0;
           }
           
 } 
 //--------------------------------------------------------------uploadfiletohdfs end---------------------------------------------------//
 
 //转换布尔值
 function transboolean($sfrewrite) 
 {
        switch($sfrewrite)
        {
                case "true":
                return 1;
                break;
                case "false":
                return 0;
                break;
        }
 }
 //--------------------------------------------------------------transboolean end--------------------------------------------------------//
 
 //uploadfiletohdfs($hdfshost,$hdfsport,"/tmp/xiha.txt","R12","xiha1.txt","true","6",$defaultbuffersize,$defaultpermission);
 //checkfile($hdfshost,$hdfsport,"home","1.pdf");
  
  // 得到hdfs中单个文件信息(以对象形式返回)
 function  getfileinfo($hdfshost,$hdfsport,$flowmediatype,$flowmedianame) 
  {
        $url = "http://".$hdfshost.":".$hdfsport."/webhdfs/v1/".$flowmediatype."/".$flowmedianame."?op=GETFILESTATUS";
            $ch = curl_init();
            curl_setopt($ch,CURLOPT_URL,$url);
            curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
            curl_setopt($ch,CURLOPT_HEADER,0);
            $data = curl_exec($ch);
            curl_close($ch);
            $obj = json_decode($data);
            //print_r($obj->FileStatus);
            return $obj;
  }
  //----------------------------------------------------------------getfileinfo end---------------------------------------//
  
  //getfileinfo($hdfshost,$hdfsport,"jiaoxue","mj.flv");
  //删除流媒体文件
  function deletefile($hdfshost,$hdfsport,$flowmediatype,$flowmedianame) 
   {
           $url = "http://".$hdfshost.":".$hdfsport."/webhdfs/v1/".$flowmediatype."/".$flowmedianame."?op=DELETE&recursive=false";
           
           $ch = curl_init();
           curl_setopt($ch,CURLOPT_URL,$url);
           curl_setopt($ch,CURLOPT_CUSTOMREQUEST,"DELETE");
           curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
           curl_setopt($ch,CURLOPT_HEADER,1);
           $data = curl_exec($ch);
           curl_close($ch);
           //print_r($data);
           if (eregi("HTTP/1.1 200 OK",$data)) 
           {
                  return 1;
           } else {
                  return 0;
           }
           
   }
  //----------------------------------------------------------------deletefile end--------------------------------------------------// 
  //deletefile($hdfshost,$hdfsport,"home","1.pdf");
  
  //得到hdfs中文件夹信息
  function getfolderinfo($hdfshost,$hdfsport,$flowmediatype) 
    {
        $url = "http://".$hdfshost.":".$hdfsport."/webhdfs/v1/".$flowmediatype."?op=GETCONTENTSUMMARY";
            $ch = curl_init();
            curl_setopt($ch,CURLOPT_URL,$url);
            curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
            curl_setopt($ch,CURLOPT_HEADER,0);
            $data = curl_exec($ch);
            curl_close($ch);
            $obj = json_decode($data);
            //print_r($obj -> ContentSummary );
            return $obj;
    }
   //getfolderinfo($hdfshost,$hdfsport,"jiaoxue");
   
   //修改副本数
   function alterreplinum($hdfshost,$hdfsport,$flowmediatype,$flowmedianame,$replinum) 
      {
          $url = "http://".$hdfshost.":".$hdfsport."/webhdfs/v1/".$flowmediatype."/".$flowmedianame."?op=SETREPLICATION&replication=".$replinum."";
          $ch = curl_init();
          curl_setopt($ch,CURLOPT_URL,$url);
          curl_setopt($ch,CURLOPT_PUT,1);
          curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
          curl_setopt($ch,CURLOPT_HEADER,1);
          $data = curl_exec($ch);
          curl_close($ch);        
          //print_r($data);
          if (eregi("HTTP/1.1 200 OK",$data)) 
           {
                  return 1;
           } else {
                  return 0;
           }
           
      }
      //alterreplinum($hdfshost,$hdfsport,"jiaoxue","171922.png","4");
?>

