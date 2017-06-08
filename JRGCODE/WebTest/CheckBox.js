
var ActionFlagStr = "";
var ActionDesrcStr = "";
var ServiceDesrcStr = "";
var ServiceCodeStr = "";


test1();

function test1() {
	var ServerAddr = "172.29.22.15:8088";
	$.getJSON("http://"+ServerAddr+"/test1?format=json&jsoncallback=?",function(data,status) {
       var DataArray = eval(data);
       for (i in DataArray) 
         {
           //alert(DataArray[i]["name"]);
           var id = DataArray[i]["id"];
           var name = DataArray[i]["name"];
           WriteCheckBoxTable(id,name);
         }
	});
}

function test2(ActionFlagStr,ServiceCodeStr) {
	var ServerAddr = "172.29.22.15:8088";
    $.getJSON("http://"+ServerAddr+"/test2?format=json&jsoncallback=?","action="+ActionFlagStr+"&bankHandleString="+ServiceCodeStr,function(data,status){
            alert(data);
    });

}

function WriteCheckBoxTable(id,name){
         $("#CheckBoxTableDiv table tbody").html(function(i,origHtml){
                  //return "<tr class='error' id='check' val="+id+"><td>"+id+"</td><td>"+url+"</td><td id='status'>Running</td><td><a  href='#' >Check</a></td></tr>" + origHtml;
                  //return "<tr class='error' id='check' val="+id+"><td>"+id+"</td><td>"+url+"</td><td id='status'>Running</td><td><a  href='#' >Check</a></td></tr>" + origHtml;
                  var str1 = "<td>"+name+"</td>"
                  var str2 = "<td><input id="+name+"@快捷 type='checkbox' name='ServiceCode' value="+id+"@1>快捷</td>"
                  var str3 = "<td><input id="+name+"@代扣 type='checkbox' name='ServiceCode' value="+id+"@2>代扣</td>"
                  return "<tr>"+str1+str2+str3+"</tr>"+ origHtml;
         });
}


// -----------------------
// Main
// -----------------------

$(document).ready(function() {

	 // -----------------

	 $("#GenJson").click(function(){
                             var ActionFlagStr = "";
                             var ActionDesrcStr = "";
                             var ServiceDesrcStr = "";
                             var ServiceCodeStr = "";

                             var ActionFlagStr = $('input[name="action"]').filter(":checked").val();
                             var ActionDesrcStr = $('input[name="action"]').filter(":checked").attr('id');

                             $('input[name="ServiceCode"]').each(function() {
                                 if($(this).prop('checked')){
                                 	BindStr = "bind@" + $(this).val()
                                 	TxStr = "tx@" +  $(this).val()
                                 	DesrcStr = $(this).attr('id')
                                    ServiceCodeStr = ServiceCodeStr + BindStr + "," + TxStr + ","
                                    ServiceDesrcStr = ServiceDesrcStr + DesrcStr + '\n'
                                 }
                             });
                             ServiceCodeStr = ServiceCodeStr.substring(0,ServiceCodeStr.length-1);
                             //alert(ServiceCodeStr);
                             //alert(ServiceDesrcStr);
                             //alert(ActionFlagStr);
                             //alert(ActionDesrcStr);
                             if (ActionFlagStr=="disableBankCard") {
                             	//$("#DesrcText").val(ActionDesrcStr+":\n"+ServiceDesrcStr+"\n"+"bankHandleString:"+"\n"+ServiceCodeStr);
                             	alert(ActionDesrcStr+":\n"+ServiceDesrcStr+"\n"+"bankHandleString:"+"\n"+ServiceCodeStr);
                             } 
                             else {
                             	//$("#DesrcText").val(ActionDesrcStr+":\n"+"所有银行");
                             	//var ServiceCodeStr = "";
                             	alert(ActionDesrcStr+":\n"+"所有银行");
                             }
                             test2(ActionFlagStr,ServiceCodeStr);
                             
            });

    // -----------------
    $("#ExecTask").click(function(){
    	test2();
    });
    
    // ------------------

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


