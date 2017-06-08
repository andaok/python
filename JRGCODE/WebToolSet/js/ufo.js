// ------------------
// Glogal Constant
// ------------------

var ServerAddr = "172.99.27.15:8080";


// -----------------
// Page Init
// -----------------

LoadBankInfo();
LoadBankExecHisInfo();

// -----------------
// Functions
// -----------------

function LoadBankInfo() {
	$.getJSON("http://"+ServerAddr+"/GetBankInfo?format=json&jsoncallback=?",function(data,status) {
       var DataArray = eval(data);
       for (i in DataArray) 
         {
           var code = DataArray[i]["code"];
           var name = DataArray[i]["name"];
           var IsOKJYT = DataArray[i]["IsOKJYT"];
           WriteBankInfoTable(i,code,name,IsOKJYT);
         }
	});
}

function LoadBankExecHisInfo() {
       $.getJSON("http://"+ServerAddr+"/GetBankExecHistory?format=json&jsoncallback=?",function(data,status) {
       for (i in data) 
         {
            var DataArray = eval('('+data[i]+')'); 

            var ExecTime = DataArray['ExecTime'];
            var action = DataArray["action"];
            var HandleDesrcStr = DataArray["HandleDesrcStr"];
            var resCode = DataArray["resCode"];
            
            $("#BankExecHisTable tbody").html(function(n,origHtml){
                  i = Number(i)+1;
                  var str1 = "<td>"+i+"</td>"
                  var str2 = "<td>"+ExecTime+"</td>"
                  var str3 = "<td>"+action+"</td>"
                  var str4 = "<td>"+HandleDesrcStr+"</td>"
                  var str5 = "<td>"+resCode+"</td>"
                  return origHtml+"<tr>"+str1+str2+str3+str4+str5+"</tr>";
            });    
         }
    });
}

function WriteBankInfoTable(num,code,name,IsOKJYT){
         $("#BankInfoTable tbody").html(function(i,origHtml){
                  var str1 = "<td>"+num+"</td>"
                  var str2 = "<td>"+code+"</td>"
                  var str3 = "<td>"+name+"</td>"
                  var str4 = "<td><input id="+name+"@中金快捷交易 type='checkbox' name='ServiceCode' value=tx@"+code+"@1>中金快捷交易</td>"
                  var str5 = "<td><input id="+name+"@中金代扣交易 type='checkbox' name='ServiceCode' value=tx@"+code+"@2>中金代扣交易</td>"
                  var str6 = "<td><input id="+name+"@所有交易通道 type='checkbox' name='ServiceCode' value=tx@"+code+"@ALL>所有交易通道</td>"
                  var str7 = "<td class='info'><input id="+name+"@中金快捷绑卡 type='checkbox' name='ServiceCode' value=bind@"+code+"@1>中金快捷绑卡</td>"
                  var str8 = "<td class='info'><input id="+name+"@中金代扣绑卡 type='checkbox' name='ServiceCode' value=bind@"+code+"@2>中金代扣绑卡</td>"
                  return origHtml+"<tr>"+str1+str2+str3+str4+str5+str6+str7+str8+"</tr>";
         });
}


function SendBankInfoToServer(ActionStr,HandleStr,HandleDesrcStr) {
    $.getJSON("http://"+ServerAddr+"/SendBankInfoToServer?format=json&jsoncallback=?","action="+ActionStr+"&bankHandleString="+HandleStr+"&HandleDesrcStr="+HandleDesrcStr,function(data,status){
            if (data.resCode == "0000") {
                alert("执行成功")
            } 
            else {
                alert("执行失败")
            }
            window.location.reload();
    });

}

function RemDupItem(StrObj,SepChar) {
    NewArray = []
    NewStrObj = ""
    StrArray = StrObj.split(SepChar)
    
    for (i=0; i<StrArray.length; i++) {
        item = StrArray[i]
        if ($.inArray(item,NewArray)==-1) {
            NewArray.push(item)
        }
    }

    for (i=0; i<NewArray.length; i++) {
        NewStrObj = NewStrObj + NewArray[i] + SepChar
    }

    NewStrObj = NewStrObj.substring(0,NewStrObj.length-1);
    return NewStrObj
}


// -----------------------
// Action Trigger Handle
// -----------------------

$(document).ready(function() {

	 // -----------------

	 $("#ConfirmInfoBtn").click(function(){
                             var ActionFlagStr = "";
                             var ActionDesrcStr = "";
                             var ServiceDesrcStr = "";
                             var ServiceCodeStr = "";
                             var ServiceDesrcStr1 = "";

                             var ActionFlagStr = $('input[name="action"]').filter(":checked").val();
                             var ActionDesrcStr = $('input[name="action"]').filter(":checked").attr('id');

                             $("#ActionStr").text("");
                             $("#HandleStr").text("");

                             $('input[name="ServiceCode"]').each(function() {
                                 if($(this).prop('checked')){

                                    CheckboxVal = $(this).val()
                                    StrArray = CheckboxVal.split("@")
                                    ServiceType = StrArray[0]
                                    BankCode = StrArray[1]
                                    ServiceFlag = StrArray[2]
                            
                                    if (ServiceFlag == "ALL") {
                                        TmpStr1 = "tx@"+BankCode+"@1"
                                        TmpStr2 = "tx@"+BankCode+"@2"
                                        TmpStr3 = "tx@"+BankCode+"@ALL"
                                        TmpDesrcStr = $(this).attr('id')
                                        ServiceCodeStr = ServiceCodeStr+TmpStr1+","+TmpStr2+","+TmpStr3+","
                                        ServiceDesrcStr = ServiceDesrcStr + TmpDesrcStr + '\n'
                                        ServiceDesrcStr1 = ServiceDesrcStr1 + TmpDesrcStr + ","  
                                    }
                                    else {
                                        DesrcStr = $(this).attr('id')
                                        ServiceCodeStr = ServiceCodeStr + CheckboxVal + ","
                                        ServiceDesrcStr = ServiceDesrcStr + DesrcStr + '\n'
                                        ServiceDesrcStr1 = ServiceDesrcStr1 + DesrcStr + ","
                                    }
        
                                 }
                                
                             });

                             ServiceCodeStr = ServiceCodeStr.substring(0,ServiceCodeStr.length-1);
                             ServiceCodeStr = RemDupItem(ServiceCodeStr,",")

                             ServiceDesrcStr1 = ServiceDesrcStr1.substring(0,ServiceDesrcStr1.length-1);

                             $("#ExecBtn").removeAttr("disabled");

                             if (ActionFlagStr=="disableBankCard") {

                                    if (ServiceCodeStr=="") {
                                          ShowStr3 = "如需禁用银行业务，请选择具体银行！"
                                          $("#ShowInfoDiv pre").text(ShowStr3);
                                          $("#ExecBtn").attr('disabled',"true");
                                    }
                                    else {
                                          ShowStr1 = ActionDesrcStr+":\n"+ServiceDesrcStr+"\n"+"bankHandleString:"+"\n"+ServiceCodeStr
                                          $("#ShowInfoDiv pre").text(ShowStr1);
                                          $("#HandleDesrcStr").text(ActionDesrcStr+":"+ServiceDesrcStr1);
                                          $("#ActionStr").text(ActionFlagStr);
                                          $("#HandleStr").text(ServiceCodeStr);
                                    }

                             } 
                             else {
                                ShowStr2 = ActionDesrcStr+":\n"+"所有银行"
                                $("#ShowInfoDiv pre").text(ShowStr2);
                                var ServiceCodeStr = "";
                                $("#HandleDesrcStr").text(ActionDesrcStr+":"+"所有银行");
                                $("#ActionStr").text(ActionFlagStr);
                                $("#HandleStr").text(ServiceCodeStr);
                             }

                     
            });

    // -----------------
    $("#ExecBtn").click(function(){
                          ActionStr = $("#ActionStr").text()
                          HandleStr = $("#HandleStr").text()
                          HandleDesrcStr = $("#HandleDesrcStr").text()
                          SendBankInfoToServer(ActionStr,HandleStr,HandleDesrcStr)
                          $("#myModal").modal("hide");

    });
    
    // -----------------
    
    $("#AllSelect").click(function(){
                             $('input[name="ServiceCode"]').each(function() {
                                 $(this).prop("checked","checked");
                             });

    	    });


    $("#RevSelect").click(function(){
                           $('input[name="ServiceCode"]').each(function() {
                                 if ($(this).prop("checked")) {
                                 	$(this).prop("checked",false);
                                 }
                                 else {
                                 	$(this).prop("checked","checked")
                                 }

                           	 });
    	    });

    // ----------------------
});


