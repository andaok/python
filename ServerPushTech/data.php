<?php

if(empty($_POST["time"]))exit();
set_time_limit(0);  // 不限制请求超时时间
$i = 0;
while (true) {
    usleep(500000); // 0.5s
    $i++;
    
    //如得到数据则马上返回数据给客户端,并结束本次请求.
    $rand = rand(1,999);
    if($rand <= 15) {
         $arr = array('success'=>'1','name'=>'xiaomi','text'=>$rand);
         echo json_encode($arr);
         exit();      
    }
    
    //服务器（$_POST['time']*0.5）秒后告诉客户端无数据.
    if ($i == $_POST['time']){
         $arr = array('success'=>'0','name'=>'xiaomi','text'=>$rand);
         echo json_encode($arr);
         exit();
    } 
 }
    
?>