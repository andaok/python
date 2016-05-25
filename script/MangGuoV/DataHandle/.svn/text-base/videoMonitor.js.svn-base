window.onload = function(){

VideoMonitor = function(){

/*
VID - 视频id
PID - 播放id
LID - 视频流id
X - 错误标志'X'
O - 动作成功标志'O'
PN - 正常播放的操作计数器
LN - 视频流切换时的计数器
XN - 视频播放发生错误时的计数器
sendStatus - 发送状态
sendEveryTime - 每次发送数据间隔
playerStatus - 1载入过程，2载入完成未播放，3播放过程中
msg - 错误信息
offset - 拖动至的位置
VID = arra[Math.floor((Math.random() * 3))]
PID = getPID()
*/
var arra = ['9527NDU'];

var VID = '9527NDU', PID = 'dio0', sg, PN = 1, LN = 1, XN = 1, sendStatus = false, msg, offset, playerStatus = 1, intval, errorFlag = false, width, height,
url = 'http://192.168.0.111/video', sendEveryTime = 10000 , _X_ = 'X', _Y_ = 'Y', _O_ = '0', _L_ = 'L', _C_ = 'C', _P_ = 'P', divId = 'cloudiyaplayer', logoUrl, videoImgUrl, failImgUrl = 'error.jpg', flowImgUrl = 'error.jpg';

playerStart();
	
//载入
function playerStart(){

var videoUrl = "../IOS/MOVIES/M3U8/playlist.m3u8", logoLink = 'http://www.google.com', swfUrl = 'sgplayer.swf' 

logoUrl = 'http://video.skygrande.com/player/current/sglogo.png';

videoImgUrl = 'cloudiya.jpg';

width = 640;

height = 360;

sg = sgplayer(divId).setup({

	width: width,
	
	height: height,

	image: videoImgUrl,

	file: videoUrl,

	logo: {

		file: logoUrl,

		link: logoLink,

		position: 'top-right',

		timeout: 20,

		linktarget: '_blank'

	},
	
	events: {

		onError : playError,

		onReady : ready,
		
		onPlay : play

	},

        provider: 'adaptive',

	flashplayer: swfUrl

}); 

var t = 0, max = 100, every =  200, flag = false,

	intval = setInterval(function(){

	if(t > max){clearInterval(intval);showFail({imgUrl : failImgUrl});playError()}//出现失败预览

	else{
	
	if(flag) {clearInterval(intval);Init()}
	
	t++;
	
	}

	}, every);

//监听是否加载成功	
function ready(){flag = true;playerStatus = 2}

/* //监听是否加载成功
sg.onReady(function(){flag = true;playerStatus = 2});

//全局监听失败信息
sg.onError(playError); */

}

//载入成功初始化
function Init(){

//显示视频预览图
function showVideoImg(){

if(true){;Normal()}

}

//检查流量并进行操作

playerActive(-4, function(res){

if(res.flow == 1){showVideoImg()}

else showFail({imgUrl : flowImgUrl},function(){alert('流量不足')});//失败出现流量预览

});

}

//正常播放操作
function Normal(){

var t;

//初始化
(function main(){

binds();

t = setInterval(broadcastIntval, sendEveryTime);

})();

//视频流切换
function changeLevel(){sendStatus = true;playerActive(1)}

//暂停
function pause(){sendStatus = false;playerActive(2)}

//拖动
function seek(e){offset = getNum(e.offset, 10);sendStatus = true;playerActive(3)}

//播放完成
function playComplete(){sendStatus = false;playerActive(4)}

//窗口关闭
function windowClose(){sendStatus = true;playerActive(5)}

//动作绑定
function binds(){

sg.onPause(pause);

sg.onLevelChange(changeLevel);

sg.onSeek(seek);

sg.onComplete(playComplete);

window.onbeforeunload = windowClose;

}

//视频播放每隔10秒传数据
function broadcastIntval(){

if(sendStatus) playerActive(0);

}

}

//播放错误监听
function playError(e){

var status;

switch(playerStatus){

	case 1 :
	
		status = -5;
		
		clearInterval(intval);
		
		showFail({imgUrl : failImgUrl});//失败出现流量预览
		
		break;

	case 2 :

		status = -3;
		
		errorFlag = true;
		
		showFail({imgUrl : logoUrl}, function(){alert('播放失败')});//失败出现初步预览图加文字
		
		break;
		
	default :
	
		status = -1;

		break;
		
}

msg = e.message;

sendStatus = false;

playerActive(status);

}

//失败提示
function showFail(data, callback){

$('#' + divId + '_wrapper').html('<img src=' + data.imgUrl + ' width="' + width +'" height="' + height + '">');

if(callback) callback();

}

//播放监听
function play(){

if(!errorFlag && playerStatus == 2) {playerStatus = 3;sendStatus = true;playerActive(-2)}

else{sendStatus = true}

}

//播放器动作数据发送,type动作类型
function playerActive(type, callback){

var key = VID + '_' + PID + '_', value, playtime;

if(type > -3) playtime = getNum(sg.getPosition());

//-5载入失败,-4检查流量,-3初次播放失败,-2初次播放成功,-1播放错误,0播放每10秒发送,1视频流切换,2视频暂停,3视频拖动,4播放完成,5窗口关闭
switch(type){

	case -5 : key += _X_; value = '{message=' + msg + '}'; break;
	
	case -4 : key += _Y_; value = '{}'; break;
	
	case -3 : key += _X_ + _O_; value = '{message=' + msg + '}'; break;
	
	case -2 : key += _O_; value = '{lid=' + getLid() + ',playtime=' + playtime + '}'; break;

	case -1 : key += _X_ + XN; value = '{playtime=' + playtime + ',message=' + msg + '}'; XN++; break;

	case 0 : key += _P_ ; value='{playtime=' + playtime + '}'; break;

	case 1 : key += _L_ + LN; value = '{lid=' + getLid() + ',playtime=' + playtime + '}'; LN++; break;
	
	case 2 : key += PN; value = '{playtime=' + playtime + ',flag="pause"}'; PN++;break;
	
	case 3 : key += PN; value = '{oldtime=' + getNum(playtime, 10) + ',playtime=' + offset + '}'; PN++; break;
	
	case 4 : key += PN; value = '{playtime=' + playtime + ',flag="end"}'; PN++;break;
	
	case 5 : key += _C_; value = '{playtime=' + playtime + '}';break;

}

//$.getJSON(url + "?callback=?", {key : key, value : value}, function(res){if(callback) callback(res)}); 

if(type == -4)

$.ajax({

	async : false,

	url : url,

	type : "GET",

	dataType : 'jsonp',

	jsonp : 'jsoncallback',

	data : {key : key, value : value},

	timeout : 1000,

	beforeSend : function(){},

	success : function(res){if(callback) callback(res)},
	
	complete : function(XMLR, textStatus){
	
	if(typeof(XMLR.responseText) != 'undefined' && callback){
	
	var res = '';

	try{
	
	res = eval('('+ XMLR.responseText +')');

	}catch(e){} 
	
	if(typeof(res) == 'object') callback(res);
	
	else callback();
	
	}
		
	},
	
	error : function(xhr){}
	
});

else if (type == 5)

$.ajax({

	async : false,

	url : url,

	type : "GET",

	dataType : 'json',

	data : {key : key, value : value}

})

else

$.get(url,{key : key, value : value});

}

//获取以10为倍数的数字
function getNum(num, type){

var newNum;

if(num == null || num == 'undefined' || !/^\d.*$/.test(num)) newNum = 0;

else{

newNum = parseInt(num);

if(type) newNum = Math.floor(newNum / 10) * 10;

}

return newNum;

}

//生成PID
function getPID(){

var str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', num, pid = '', i = 0;

for(;i < 4;){

num = parseInt(Math.random() * 40);

num = isNaN(num) ? 0 : num;

if(num <= 0) continue;

if(num > 0 && num < 26) pid += str.slice(num - 1, num);

else if(num >= 26) pid += num.toString().slice(-1);

i++;

}

return pid;

}

//获取视频流id
function getLid(){

var id = sg.getLevel();

return id;

}

//画图调用
function draw(){



}

};

new VideoMonitor();

};
